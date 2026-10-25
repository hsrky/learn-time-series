import numpy as np

rng = np.random.default_rng(5)
Y = rng.normal(size=(40, 24))
MU = Y + rng.normal(scale=0.3, size=Y.shape)
SG = rng.uniform(0.2, 2.0, size=Y.shape)
MK = (rng.uniform(size=Y.shape) > 0.3).astype(float)

CASES = [
    {"name": "perfect mean, sigma 1", "call": "gaussian_nll(np.array([0.0]), np.array([0.0]), np.array([1.0]))", "visible": True},
    {"name": "two sigma away", "call": "gaussian_nll(np.array([2.0]), np.array([0.0]), np.array([1.0]))", "visible": True},
    {"name": "mask drops a point", "call": "gaussian_nll(np.array([0.0, 100.0]), np.array([0.0, 0.0]), np.array([1.0, 1.0]), np.array([1, 0]))", "visible": True},
    {"name": "small sigma, big error", "call": "gaussian_nll(np.array([1.0]), np.array([0.0]), np.array([0.1]))"},
    {"name": "everything masked", "call": "gaussian_nll(np.array([1.0, 2.0]), np.array([0.0, 0.0]), np.array([1.0, 1.0]), np.zeros(2))"},
    {"name": "empty", "call": "gaussian_nll(np.array([]), np.array([]), np.array([]))"},
    {"name": "random 2D", "call": "gaussian_nll(Y, MU, SG)"},
    {"name": "random 2D with mask", "call": "gaussian_nll(Y, MU, SG, MK)"},
]
