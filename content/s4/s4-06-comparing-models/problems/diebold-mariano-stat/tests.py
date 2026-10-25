import numpy as np

rng = np.random.default_rng(5)
A = rng.normal(0, 2.0, 300)
B = rng.normal(0, 1.5, 300)
# overlapping 5-step errors are autocorrelated: build them from a moving sum
NOISE = rng.normal(0, 1, 304)
C = np.convolve(NOISE, np.ones(5), "valid")
D = np.convolve(rng.normal(0, 1, 304), np.ones(5), "valid") * 0.9

CASES = [
    {"name": "constant difference gives nan", "call": "dm_test([1, -1, 1, -1], [2, -2, 2, -2])", "visible": True,
     "expected": "{'stat': float('nan'), 'p_value': float('nan')}"},
    {"name": "absolute loss example", "call": "dm_test([1, 2, 1, 2], [2, 2, 2, 3], h=1, power=1)", "visible": True,
     "expected": "{'stat': -0.75 / (0.1875 / 4) ** 0.5, 'p_value': 0.0005320}", "tol": 1e-4},
    {"name": "too short", "call": "dm_test([1.0], [2.0])", "visible": True,
     "expected": "{'stat': float('nan'), 'p_value': float('nan')}"},
    {"name": "equal models", "call": "dm_test(A, A)", "expected": "{'stat': float('nan'), 'p_value': float('nan')}"},
    {"name": "swap changes the sign", "call": "dm_test(B, A)"},
    {"name": "model 2 is worse", "call": "dm_test(A, B)"},
    {"name": "horizon 5 with autocorrelation", "call": "dm_test(C, D, h=5)"},
    {"name": "horizon 5, absolute loss", "call": "dm_test(C, D, h=5, power=1)"},
]
