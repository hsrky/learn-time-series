import numpy as np

_r = np.random.default_rng(21)
BIG = (50 + np.cumsum(_r.normal(0, 1, 5000))).tolist()

CASES = [
    {"name": "lesson example", "call": "ses([10, 14, 12, 16], 0.5, 2)", "visible": True},
    {"name": "constant series", "call": "ses([5, 5, 5], 0.3, 3)", "visible": True},
    {"name": "alpha 1 is naive", "call": "ses([3, 9, 4, 7], 1.0, 1)", "expected": "{'level': [3.0, 9.0, 4.0, 7.0], 'forecast': [7.0]}"},
    {"name": "alpha 0 keeps the first value", "call": "ses([3, 9, 4, 7], 0.0, 2)", "expected": "{'level': [3.0, 3.0, 3.0, 3.0], 'forecast': [3.0, 3.0]}"},
    {"name": "single value", "call": "ses([8], 0.4, 3)", "expected": "{'level': [8.0], 'forecast': [8.0, 8.0, 8.0]}"},
    {"name": "h = 0", "call": "ses([1, 2, 3], 0.5, 0)"},
    {"name": "5000 random-walk points", "call": "ses(BIG, 0.2, 5)"},
]
