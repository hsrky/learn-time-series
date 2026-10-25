import numpy as np

rng = np.random.default_rng(0)
T = np.arange(300)
S = 10 + 3 * np.sin(2 * np.pi * T / 12) + 0.02 * T + rng.normal(0, 0.3, 300)

CASES = [
    {"name": "straight line", "call": "direct_forecast([1, 2, 3, 4, 5, 6], 2, 3)", "visible": True,
     "expected": "np.array([7.0, 8.0, 9.0])", "tol": 1e-6},
    {"name": "two steps on a line", "call": "direct_forecast([1, 2, 3, 4], 1, 2)", "visible": True,
     "expected": "np.array([5.0, 6.0])", "tol": 1e-6},
    {"name": "constant series", "call": "direct_forecast([5, 5, 5, 5, 5], 2, 2)", "visible": True,
     "expected": "np.array([5.0, 5.0])", "tol": 1e-6},
    {"name": "step without rows is nan", "call": "direct_forecast([1, 2, 3, 4], 1, 5)[3:]", "expected": "np.array([np.nan, np.nan])"},
    {"name": "step 1 equals the recursive first step", "call": "direct_forecast([1, 4, 9, 16, 25, 36, 49], 3, 1)"},
    {"name": "doubling series", "call": "direct_forecast([2, 4, 8, 16, 32, 64], 1, 3)"},
    {"name": "season 12", "call": "direct_forecast(S, 12, 12)", "tol": 1e-5},
    {"name": "short series with long horizon", "call": "direct_forecast(S[:20], 6, 10)", "tol": 1e-5},
    {"name": "long horizon", "call": "direct_forecast(S[:150], 8, 60)", "tol": 1e-5},
]
