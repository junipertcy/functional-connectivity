import networkx as nx
import numpy as np
from scipy import sparse
from dataclasses import dataclass
import datetime


@dataclass
class GraphStorage:
    g: nx.Graph
    precision_mat: sparse.csr_matrix
    correlation_mat: sparse.csr_matrix
    adj_mat: sparse.csr_matrix

    def __init__(self, g: nx.Graph):
        self.g = g
        self.adj_mat = nx.adjacency_matrix(self.g)
        self.precision_mat = self.adj_mat + sparse.eye(self.adj_mat.shape[0])
        self.correlation_mat = sparse.linalg.inv(self.precision_mat)

    def __str__(self):
        return "GraphStorage(%s)" % self.g

    # need a __repr__ method to print things out elegantly


class DataHandler(GraphStorage):
    def __init__(self, sparse=True):
        self.inverse_sigmas = []
        self.sigmas = []
        self.network_files = []
        self.graphs = []
        self.num_nodes = 0
        self.graph_paths = []

    def from_edgelist(self, path, comments="#", delimiter=" "):
        self.graph_paths.append(path)
        g = nx.read_edgelist(
            path,
            comments=comments,
            delimiter=delimiter,
            nodetype=int,
            data=(("weight", float),),
        )
        if g.number_of_nodes() > self.num_nodes:
            self.num_nodes = g.number_of_nodes()

        self.graphs.append(GraphStorage(g))
        return GraphStorage(g)

    def generate_mvn(self, counts=[100, 100], save_to_file=False):
        if len(counts) is not len(self.graphs):
            raise ValueError("Counts do not match the number of networks.")

        z = np.zeros((self.num_nodes, sum(counts)), dtype=np.float64)
        cumsum_z = np.cumsum(counts)
        for idx, (graph, count) in enumerate(zip(self.graphs, counts)):
            x = np.random.multivariate_normal(
                np.zeros(self.num_nodes),  # TODO: generalize this
                graph.correlation_mat.todense(),
                count,
            ).T
            if idx == 0:
                z[:, : cumsum_z[idx]] = x
            else:
                z[:, cumsum_z[idx - 1] : cumsum_z[idx]] = x

        if save_to_file:
            _datetime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            filename = (
                f"synthetic_data/{sum(counts)}-{'_'.join([str(i) for i in counts])}-n_{self.num_nodes}-{_datetime}.csv"
            )

            print("Saving data to %s" % filename)
            graph_paths = " ".join(self.graph_paths)
            np.savetxt(filename, z, delimiter=",", header=f"Data generated from networks:{graph_paths}")
        return z
