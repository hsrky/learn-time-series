import numpy as np

rng = np.random.default_rng(0)
T = np.arange(300)
S = 10 + 3 * np.sin(2 * np.pi * T / 12) + 0.02 * T + rng.normal(0, 0.3, 300)

CASES = [
    {"name": "straight line", "call": "recursive_forecast([1, 2, 3, 4, 5, 6], 2, 3)", "visible": True,
     "expected": "np.array([7.0, 8.0, 9.0])", "tol": 1e-6},
    {"name": "constant series", "call": "recursive_forecast([5, 5, 5, 5], 1, 2)", "visible": True,
     "expected": "np.array([5.0, 5.0])", "tol": 1e-6},
    {"name": "AR(1) on doubling", "call": "recursive_forecast([2, 4, 8, 16, 32], 1, 2)", "visible": True},
    {"name": "p equals 3, h equals 1", "call": "recursive_forecast([1, 4, 9, 16, 25, 36, 49], 3, 1)"},
    {"name": "p = n - 1 (one training row)", "call": "recursive_forecast([1.0, 2.0, 3.5], 2, 2)"},
    {"name": "season 12, p = 12", "call": "recursive_forecast(S, 12, 24)", "tol": 1e-5},
    {"name": "season 12, p = 6", "call": "recursive_forecast(S[:200], 6, 6)", "tol": 1e-5},
    {"name": "long horizon", "call": "recursive_forecast(S[:100], 4, 50)", "tol": 1e-5},
]
