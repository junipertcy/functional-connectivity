try:
    import graph_tool.all as gt
except ImportError:
    pass

import datetime
import sys
from dataclasses import dataclass

import networkx as nx
import numpy as np
from scipy import sparse


@dataclass
class GraphStorage:
    g: nx.Graph or nx.DiGraph
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

    def __repr__(self):
        t = type(self.g)
        return f"{t} object, with {self.g.number_of_nodes()} nodes and {self.g.number_of_edges()} edges, at {hex(id(self.g))}"

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

    # """ Reads a network in given file and generates
    #     inverse covariance matrices. Expected format for
    #     networks in given files is:
    #     [start node index],[end node index],[edge weight]  """

    # def read_network(self, filename, comment="#", splitter=",", inversion=True):
    #     nodes = []
    #     self.network_files.append(filename)
    #     with open(filename, "r") as f:
    #         for i, line in enumerate(f):
    #             if comment in line:
    #                 continue
    #             data = line.split(splitter)
    #             if data[0] not in nodes:
    #                 nodes.append(int(data[0]))
    #             if data[1] not in nodes:
    #                 nodes.append(int(data[1]))
    #     self.dimension = max(nodes)
    #     network = np.eye(self.dimension)
    #     with open(filename, "r") as f:
    #         for i, line in enumerate(f):
    #             if comment in line:
    #                 continue
    #             data = line.split(splitter)
    #             network[int(data[0]) - 1, int(data[1]) - 1] = float(data[2])
    #             network[int(data[1]) - 1, int(data[0]) - 1] = float(data[2])
    #     self.inverse_sigmas.append(network)
    #     if inversion:
    #         sigma = np.linalg.inv(network)
    #         print(np.linalg.eigvals(sigma))
    #         self.sigmas.append(sigma)
    #         print(sigma)
    #         print(np.shape(sigma))
    #         print(network)
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
            filename = f"synthetic_data/{sum(counts)}-{'_'.join([str(i) for i in counts])}-n_{self.num_nodes}-{_datetime}.csv"

            print("Saving data to %s" % filename)
            graph_paths = " ".join(self.graph_paths)
            np.savetxt(
                filename,
                z,
                delimiter=",",
                header=f"Data generated from networks:{graph_paths}",
            )
        return z

    """ Generates a data file (.csv) from networks previously defined in
        self.sigmas (covariance matrix) """

    def generate_real_data(self, counts=[100, 100]):
        if len(counts) is not len(self.sigmas):
            raise Exception("Lengths of networks and data lengths do not match.")
        z = None
        total_count = 0
        for sigma, datacount in zip(self.sigmas, counts):
            x = np.random.multivariate_normal(
                np.zeros(self.dimension), sigma, datacount
            )
            total_count += datacount
            if z is None:
                z = x
            else:
                z = np.vstack((z, x))
        filename = "synthetic_data/{}x{}_{}.csv".format(
            total_count,
            self.dimension,
            datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
        )
        header = "# Data generated from networks:\n# "
        for f, datacount in zip(self.network_files, counts):
            header += f"{f}: {datacount}, "
        header = header[:-2]
        header += "\n"
        with open(filename, "w") as new_file:
            new_file.write(header)
            for datarow in z:
                line = ""
                for value in datarow:
                    line += "," + str(f"{value:.4f}")
                line = line[1:]
                new_file.write("%s\n" % line)

    """ Converts a network into matrix form """

    def write_network_to_matrix_form(self, datafile):
        new_filename = datafile.split(".")[0] + "_matrix.csv"
        self.read_network(datafile, inversion=False)
        with open(new_filename, "w") as f:
            for sig in self.inverse_sigmas:
                for i in range(np.shape(sig)[0]):
                    for j in range(np.shape(sig)[0]):
                        f.write(str(sig[i, j]) + ",")
                    f.write("\n")
                f.write("\n\n")

    """ Creates a file containing results, with network details,
        from converged algorithm instance """

    def write_network_results(self, datafile, solver, splitter=","):
        run_time = datetime.datetime.now()
        results_name = "network_results/{}_la{}be{}_{}.csv".format(
            solver.__class__.__name__,
            int(solver.lambd),
            int(solver.beta),
            run_time.strftime("%Y%m%d%H%M%S"),
        )
        """ Read features """
        with open(datafile) as f:
            for i, line in enumerate(f):
                if i == 0:
                    feats = line.strip().split(splitter)[1:]
                    break
        features = {}
        for i, feat in enumerate(feats):
            features[i] = feat
        """ Write Results """
        with open(results_name, "w") as f:
            f.write("# Information\n")
            f.write("Run datetime, %s\n" % run_time.strftime("%Y-%m-%d %H:%M:%S"))
            f.write("Data file, %s\n" % datafile)
            f.write("Solver type, %s\n" % solver.__class__.__name__)
            f.write("Penalty function, %s\n" % solver.penalty_function)
            f.write("Data dimension, %s\n" % solver.dimension)
            f.write("Blocks, %s\n" % solver.blocks)
            f.write("Observations in a block, %s\n" % solver.obs)
            f.write("Rho, %s\n" % solver.rho)
            f.write("Beta, %s\n" % solver.beta)
            f.write("Lambda, %s\n" % solver.lambd)
            f.write("Processes used, %s\n" % solver.processes)
            f.write("\n")
            f.write("# Results\n")
            f.write("Algorithm run time, %s seconds\n" % solver.run_time)
            f.write("Iterations to complete, %s\n\n" % solver.iteration)
            try:
                f.write(
                    "Temporal deviations ratio (max/mean), {:.3f}\n".format(
                        solver.dev_ratio
                    )
                )
            except ValueError:
                f.write("Temporal deviations ratio (max/mean), %s\n" % solver.dev_ratio)
            f.write("Temporal deviations ")
            for dev in solver.deviations:
                try:
                    f.write(f",{dev:.3f}")
                except ValueError:
                    f.write(",%s" % dev)
            f.write("\nNormalized Temporal deviations ")
            for dev in solver.norm_deviations:
                try:
                    f.write(f",{dev:.3f}")
                except ValueError:
                    f.write(",%s" % dev)
            """ Write networks """
            f.write("\n\n#Networks:\n\n")
            for k in range(solver.blocks):
                f.write("Block %s," % k)
                f.write(solver.blockdates[k] + "\n")
                if k > 0:
                    f.write("Dev to prev,")
                    f.write(f"{solver.deviations[k - 1]:.3f},")
                if k < solver.blocks - 1:
                    f.write("Dev to next,")
                    f.write(f"{solver.deviations[k]:.3f}")
                f.write("\n")
                for feat in feats:
                    f.write("," + feat)
                f.write("\n")
                for i in range(solver.dimension):
                    f.write(features[i])
                    for j in range(solver.dimension):
                        f.write("," + str(solver.thetas[k][i, j]))
                    f.write("\n")
                f.write("\n\n")

    """ Creates a file containing results, without network details,
        from converged solver instance """

    def write_results(self, datafile, solver, splitter=","):
        run_time = datetime.datetime.now()
        results_name = "results/{}_la{}be{}_{}.csv".format(
            solver.__class__.__name__,
            int(solver.lambd),
            int(solver.beta),
            run_time.strftime("%Y%m%d%H%M%S"),
        )
        with open(results_name, "w") as f:
            f.write("# Information\n")
            f.write("Run datetime, %s\n" % run_time.strftime("%Y-%m-%d %H:%M:%S"))
            f.write("Data file, %s\n" % datafile)
            f.write("Solver type, %s\n" % solver.__class__.__name__)
            f.write("Penalty function, %s\n" % solver.penalty_function)
            f.write("Data dimension, %s\n" % solver.dimension)
            f.write("Blocks, %s\n" % solver.blocks)
            f.write("Observations in a block, %s\n" % solver.obs)
            f.write("Rho, %s\n" % solver.rho)
            f.write("Beta, %s\n" % solver.beta)
            f.write("Lambda, %s\n" % solver.lambd)
            f.write("Processes used, %s\n" % solver.processes)
            f.write("Total edges, %s\n" % solver.real_edges)
            f.write("Total edgeless, %s\n" % solver.real_edgeless)
            f.write("\n")
            f.write("# Results\n")
            f.write("Algorithm run time, %s seconds\n" % solver.run_time)
            f.write("Iterations to complete, %s\n\n" % solver.iteration)
            f.write("Correct positive edges, %s\n" % solver.correct_positives)
            f.write("All positives, %s\n" % solver.all_positives)
            f.write(f"F1 Score, {solver.f1score:.3f}\n")
            try:
                f.write(
                    "Temporal deviations ratio (max/mean), {:.3f}\n".format(
                        solver.dev_ratio
                    )
                )
            except ValueError:
                f.write("Temporal deviations ratio (max/mean), %s\n" % solver.dev_ratio)
            f.write("Temporal deviations ")
            for dev in solver.deviations:
                try:
                    f.write(f",{dev:.3f}")
                except ValueError:
                    f.write(",%s" % dev)
            f.write("\nNormalized Temporal deviations ")
            for dev in solver.norm_deviations:
                try:
                    f.write(f",{dev:.3f}")
                except ValueError:
                    f.write(",%s" % dev)
            f.write("\n")


if __name__ == "__main__" and len(sys.argv) % 2 == 1:
    # Input arguments need to be pairwise.
    # First item of the pair is the network file.
    # Second item of the pair is number of datapoints
    # to create from the given network.
    # Arbitrary number of pair can be inputted.

    dh = DataHandler()
    data_counts = []
    for i in range(1, len(sys.argv), 2):
        dh.read_network(sys.argv[i])
        data_counts.append(int(sys.argv[i + 1]))
    if len(data_counts) > 0:
        dh.generate_real_data(data_counts)
