import numpy as np

A = np.arange(6.0)
B = np.arange(8.0)
M = np.column_stack([np.arange(10.0), np.arange(10.0) * 10])
rng = np.random.default_rng(7)
BIG = rng.normal(size=(500, 3))

CASES = [
    {"name": "6 points, 3 in, 2 out", "call": "make_windows(A, 3, 2)", "visible": True},
    {"name": "stride 3", "call": "make_windows(B, 2, 1, stride=3)", "visible": True},
    {"name": "two features", "call": "make_windows(M, 4, 2)", "visible": True},
    {"name": "exact fit: one window", "call": "make_windows(A, 4, 2)"},
    {"name": "too short: empty", "call": "make_windows(np.arange(4.0), 3, 2)"},
    {"name": "empty series", "call": "make_windows(np.array([]), 3, 1)"},
    {"name": "stride bigger than series", "call": "make_windows(B, 2, 2, stride=50)"},
    {"name": "random 500x3, stride 7", "call": "make_windows(BIG, 48, 12, stride=7)"},
]
