import numpy as np

rng = np.random.default_rng(5)
N = 3000
AR1 = np.zeros(N)
AR2 = np.zeros(N)
e = rng.normal(size=N)
for t in range(2, N):
    AR1[t] = 0.7 * AR1[t - 1] + e[t]
    AR2[t] = 0.5 * AR2[t - 1] + 0.3 * AR2[t - 2] + e[t]

CASES = [
    {"name": "short series, 2 lags", "call": "pacf([1, 3, 2, 4, 3, 5, 4, 6], 2)", "visible": True},
    {"name": "lag 1 equals acf", "call": "pacf([2.0, 5.0, 3.0, 8.0, 6.0], 1)", "visible": True},
    {"name": "constant series", "call": "pacf([3, 3, 3, 3, 3], 2)", "expected": "np.array([1.0, 0.0, 0.0])"},
    {"name": "AR(1) cuts off", "call": "pacf(AR1, 5)", "tol": 1e-8},
    {"name": "AR(2) cuts off after 2", "call": "pacf(AR2, 6)", "tol": 1e-8},
    {"name": "many lags", "call": "pacf(AR2, 30)", "tol": 1e-8},
    {"name": "AR(1) value near phi", "call": "round(float(pacf(AR1, 3)[1]), 1)", "expected": "0.7"},
]
