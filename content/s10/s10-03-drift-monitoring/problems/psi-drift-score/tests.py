import numpy as np

A8 = [1, 2, 3, 4, 5, 6, 7, 8]
rng = np.random.default_rng(5)
TR = rng.normal(0, 1, 3000)
SAME = rng.normal(0, 1, 1500)
SHIFT = rng.normal(0.5, 1.3, 1500)
TIES = np.repeat([1, 2, 3], 50)

CASES = [
    {"name": "identical samples", "call": "psi(A8, A8, bins=4)", "expected": "0.0", "visible": True},
    {"name": "all actual above the median", "call": "psi(A8, [7, 7, 8, 8], bins=2)", "visible": True,
     "expected": "(0.0001 - 0.5) * math.log(0.0001 / 0.5) + (1.0 - 0.5) * math.log(1.0 / 0.5)"},
    {"name": "book example shares", "call": "psi(np.arange(100), np.repeat([12, 37, 62, 87], [10, 20, 30, 40]), bins=4)",
     "visible": True, "expected": "0.22826", "tol": 1e-4},
    {"name": "no drift, large", "call": "psi(TR, SAME)"},
    {"name": "shifted, large", "call": "psi(TR, SHIFT, bins=10)"},
    {"name": "ties in training data", "call": "psi(TIES, [1, 1, 2, 3, 3, 3], bins=3)"},
    {"name": "single bin is always 0", "call": "psi(TR, SHIFT, bins=1)", "expected": "0.0"},
    {"name": "empty bin is clipped", "call": "psi(A8, [1, 1, 1, 1], bins=4)"},
]
