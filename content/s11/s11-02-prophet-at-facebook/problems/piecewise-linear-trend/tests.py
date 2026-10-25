import numpy as np

Y1 = [0, 1, 2, 3, 4, 3, 2, 1]
rng = np.random.default_rng(13)
n = 400
t = np.arange(n)
YB = 5 + 0.3 * t + 0.5 * np.maximum(0, t - 120) - 1.2 * np.maximum(0, t - 260) + rng.normal(0, 2, n)

CASES = [
    {"name": "perfect V shape with forecast", "call": "piecewise_trend(Y1, [4], 2)", "visible": True,
     "expected": "np.array([0, 1, 2, 3, 4, 3, 2, 1, 0, -1.0])"},
    {"name": "no changepoints is a straight line", "call": "piecewise_trend([1, 3, 5, 7], [], 1)", "visible": True,
     "expected": "np.array([1, 3, 5, 7, 9.0])"},
    {"name": "noisy fit, no horizon", "call": "np.round(piecewise_trend([1, 2, 2, 4, 5, 5, 8, 9], [3]), 6)", "visible": True},
    {"name": "two changepoints", "call": "piecewise_trend([0, 2, 4, 4, 4, 2, 0, -2, -4], [2, 5], 3)"},
    {"name": "constant series", "call": "piecewise_trend([4, 4, 4, 4, 4], [2], 2)", "expected": "np.full(7, 4.0)"},
    {"name": "large noisy series", "call": "piecewise_trend(YB, [120, 260], 30)", "tol": 1e-6},
    {"name": "large series, wrong changepoints still fits", "call": "piecewise_trend(YB, [100, 200, 300], 10)"},
]
