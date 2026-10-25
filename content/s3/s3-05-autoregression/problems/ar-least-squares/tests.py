import numpy as np

_r = np.random.default_rng(11)
N = 2000
AR2 = np.zeros(N)
for _t in range(2, N):
    AR2[_t] = 2 + 0.5 * AR2[_t - 1] + 0.3 * AR2[_t - 2] + _r.normal()
AR1 = np.zeros(500)
for _t in range(1, 500):
    AR1[_t] = -1 + 0.7 * AR1[_t - 1] + _r.normal(0, 0.5)

CASES = [
    {"name": "perfect line", "call": "fit_ar([1, 2, 3, 4, 5, 6], 1)", "visible": True},
    {"name": "AR(2) simulated", "call": "fit_ar(AR2, 2)", "visible": True, "tol": 1e-6},
    {"name": "AR(1) with negative constant", "call": "fit_ar(AR1, 1)"},
    {"name": "alternating series", "call": "fit_ar([1, -1, 1, -1, 1, -1, 1, -1], 1)", "expected": "np.array([0.0, -1.0])", "tol": 1e-6},
    {"name": "exact AR(2) recurrence (Fibonacci)", "call": "fit_ar([1, 1, 2, 3, 5, 8, 13, 21, 34], 2)", "expected": "np.array([0.0, 1.0, 1.0])", "tol": 1e-6},
    {"name": "p = 3 on simulated data", "call": "fit_ar(AR2, 3)", "tol": 1e-6},
    {"name": "length of result", "call": "len(fit_ar(AR2, 5))", "expected": "6"},
]
