import numpy as np

rng = np.random.default_rng(3)
N = 2000
AR = np.zeros(N)
for t in range(1, N):
    AR[t] = 0.8 * AR[t - 1] + rng.normal()

CASES = [
    {"name": "small example", "call": "acf([1, 3, 2, 4, 3], 2)", "visible": True},
    {"name": "trend", "call": "acf([1, 2, 3, 4, 5, 6], 3)", "visible": True},
    {"name": "lag 0 only", "call": "acf([5, 1, 7], 0)", "expected": "np.array([1.0])"},
    {"name": "constant series", "call": "acf([4, 4, 4, 4], 2)", "expected": "np.array([1.0, 0.0, 0.0])"},
    {"name": "alternating", "call": "acf([1, -1, 1, -1, 1, -1], 2)"},
    {"name": "max lag n-1", "call": "acf([2, 9, 4, 4], 3)"},
    {"name": "AR(1) phi 0.8, 2000 points", "call": "acf(AR, 10)", "tol": 1e-9},
]
