import numpy as np
import numba as nb
import scipy.sparse as spr


def compute_std(samples):
    return np.std(samples, axis=1)


def generateRandom(n, density, id_addition=1e-16):
    A_rand = spr.random(n, n, np.sqrt(density * n / 100) / n).toarray()
    A = np.zeros((n, n), dtype="float64")
    A[A_rand != 0] += -1
    A[A_rand > 0.5] += 2
    A = A.T @ A
    d = np.diag(A).copy()
    A -= np.diag(d)
    A[A > 1] = 1
    A[A < -1] = -1
    A += np.diag(d)
    lmin = getLambdaMin(A)
    delta = np.max((-1.2 * lmin, id_addition))
    A = A + delta * spr.eye(n)
    return spr.coo_matrix(A)


def normlize_data(samples, mean, std):
    mean_mat = np.repeat(mean.reshape(-1, 1), axis=1, repeats=samples.shape[1])
    samples = samples - mean_mat
    std_mat = np.diag(1 / std)
    samples = std_mat @ samples
    return samples


def cal_S(samples):
    n = samples.shape[0]
    _samples = samples.shape[1]
    S = np.zeros((n, n), dtype="float64")
    for i in range(_samples):
        y_i = samples[:, i].reshape(-1, 1)
        S += y_i @ y_i.T
    S /= _samples
    return S


def getLambdaMin(A):
    return np.linalg.eigvalsh(A)[0]


def normlize_sig_inv(sig_inv, std):
    std_mat = np.diag(std)
    return std_mat @ sig_inv @ std_mat


def generate_samples(Sigma_inv, samples=1):
    n = Sigma_inv.shape[0]
    L_inv = np.linalg.inv(np.linalg.cholesky(Sigma_inv))
    xs = np.random.normal(0, 1, [samples, n])
    samples = L_inv.T @ xs.T
    return samples


def compute_mean(samples):
    return np.mean(samples, axis=1)


class GraphicalGenerator:
    def __init__(
        self,
        N,
        type="random",
        type_param=0.1,
        n_samples=10,
        normalize=True,
        batch=3,
        constant=True,
        id_addition=1,
        precision_mat=None,
    ):
        """Generate test fixtures for experimental uses.

        Args:
            N (interger): Dimension of the graph (i.e., number of nodes).
            type (string): Type of the graph to generate.
            type_param (double): Parameter for the type of the graph.
            n_samples (integer): Number of samples to generate.
            normalize (boolean): Whether to normalize the data. Default to True.
            batch (interger): Number of independent samples to generate.
            constant (boolean): Whether to fix the generated graph and samples. Default to True.
            id_addition (int): Trick to make the precision matrix positive definite.
            precision_mat (boolean): Whether to generate data with a predefined precision matrix. Defaults to None.
        """
        self.N = N
        self.type = type
        self.type_param = type_param
        self.n_samples = n_samples
        self.normalize = normalize
        self.batch = batch
        self.constant = constant
        self.precision_mat = precision_mat
        self.sig_exist = precision_mat is not None
        self.id_addition = id_addition

        self.precision_mat_list = []
        self.ss_list = []
        self.samples_list = []
        if self.constant:
            for _ in range(self.batch):
                self.generate()

    def __call__(self):
        if self.constant:
            return self.precision_mat_list, self.ss_list

        self.precision_mat_list = []
        self.ss_list = []
        self.samples_list = []
        for _ in range(self.batch):
            self.generate()

        return self.precision_mat_list, self.ss_list, self.samples_list

    def generate(self):
        if self.sig_exist:
            self.precision_mat_list += [self.precision_mat.astype("float32")]
        elif self.type == "random":
            self.precision_mat_list += [
                generateRandom(self.N, self.type_param, self.id_addition)
                .toarray()
                .astype("float32")
            ]
        samples = np.random.randint(low=self.n_samples, high=self.n_samples + 1)
        samples = generate_samples(self.precision_mat_list[-1], samples)

        if self.normalize:
            mean = compute_mean(samples)
            std = compute_std(samples)
            samples = normlize_data(samples, mean, std)
            self.precision_mat_list[-1] = normlize_sig_inv(
                self.precision_mat_list[-1], std
            ).astype("float32")
        self.ss_list += [cal_S(samples).astype("float32")]
        self.samples_list += [samples.astype("float32")]


class GraphicalGeneratorTV(GraphicalGenerator):
    def __init__(
        self,
        N,
        type="random",
        type_param=0.1,
        n_samples=10,
        normalize=True,
        batch=3,
        constant=True,
        id_addition=1,
        precision_mat=None,
    ):
        super().__init__(
            N,
            type,
            type_param,
            n_samples,
            normalize,
            batch,
            constant,
            id_addition,
            precision_mat,
        )

    pass
