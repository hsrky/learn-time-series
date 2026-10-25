import numpy as np

rng = np.random.default_rng(9)
Y = rng.gamma(3.0, 10.0, 500)
Q10 = Y.mean() * 0.6 + np.zeros(500)
Q50 = np.full(500, np.median(Y))
Q90 = np.full(500, np.quantile(Y, 0.9))

CASES = [
    {"name": "forecast too low", "call": "pinball_loss([100], [90], 0.9)", "visible": True, "expected": "9.0"},
    {"name": "forecast too high", "call": "pinball_loss([100], [110], 0.9)", "visible": True, "expected": "1.0"},
    {"name": "median is half of MAE", "call": "pinball_loss([1, 5, 9], [2, 5, 6], 0.5)", "visible": True,
     "expected": "0.5 * (1 + 0 + 3) / 3"},
    {"name": "empty", "call": "pinball_loss([], [], 0.5)", "expected": "float('nan')"},
    {"name": "perfect", "call": "pinball_loss([3, 4], [3, 4], 0.1)", "expected": "0.0"},
    {"name": "arrays, tau 0.1", "call": "pinball_loss(np.array([10.0, 20.0, 30.0]), np.array([12.0, 18.0, 33.0]), 0.1)",
     "expected": "(0.9 * 2 + 0.1 * 2 + 0.9 * 3) / 3"},
    {"name": "weighted loss small", "call": "weighted_quantile_loss([10, 20], [[8, 22], [12, 18]], [0.1, 0.9])"},
    {"name": "weighted loss zero total", "call": "weighted_quantile_loss([0, 0], [[1, 1]], [0.5])", "expected": "float('nan')"},
    {"name": "random data, three levels", "call": "weighted_quantile_loss(Y, [Q10, Q50, Q90], [0.1, 0.5, 0.9])"},
    {"name": "random data, tau 0.9", "call": "pinball_loss(Y, Q90, 0.9)"},
]
