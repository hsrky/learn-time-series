import numpy as np

T = np.arange(0, 50)
_r = np.random.default_rng(14)
T_RAND = _r.uniform(0, 1000, 400)

CASES = [
    {"name": "period 4, K = 1", "call": "fourier_features([0, 1, 2], 4, 1)", "visible": True, "tol": 1e-9},
    {"name": "names", "call": "fourier_names('week', 2)", "visible": True},
    {"name": "K = 0 gives no columns", "call": "fourier_features([0, 1, 2], 7, 0).shape", "expected": "(3, 0)"},
    {"name": "weekly K = 3 shape", "call": "fourier_features(T, 7, 3).shape", "expected": "(50, 6)"},
    {"name": "weekly K = 3 values", "call": "fourier_features(T, 7, 3)", "tol": 1e-9},
    {"name": "yearly period 365.25, K = 2", "call": "fourier_features(T_RAND, 365.25, 2)", "tol": 1e-9},
    {"name": "rows repeat after one period", "call": "np.allclose(fourier_features([2, 9], 7, 3)[0], fourier_features([2, 9], 7, 3)[1])", "expected": "True"},
    {"name": "empty input", "call": "fourier_features([], 7, 2).shape", "expected": "(0, 4)"},
    {"name": "names for K = 0", "call": "fourier_names('x', 0)", "expected": "[]"},
]
