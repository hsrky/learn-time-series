import numpy as np

rng = np.random.default_rng(2)
BIG = rng.normal(size=1000)

CASES = [
    {"name": "basic", "call": "make_windows([3, 5, 4, 6, 8, 7], 3, 1)", "visible": True,
     "expected": "(np.array([[3, 5, 4], [5, 4, 6], [4, 6, 8]], dtype=float), np.array([[6], [8], [7]], dtype=float))"},
    {"name": "horizon 2 and stride 2", "call": "make_windows([1, 2, 3, 4, 5, 6, 7], 2, 2, 2)", "visible": True,
     "expected": "(np.array([[1, 2], [3, 4]], dtype=float), np.array([[3, 4], [5, 6]], dtype=float))"},
    {"name": "exactly one row", "call": "make_windows([1, 2, 3], 2, 1)", "visible": True,
     "expected": "(np.array([[1, 2]], dtype=float), np.array([[3]], dtype=float))"},
    {"name": "too short", "call": "make_windows([1, 2, 3], 3, 1)",
     "expected": "(np.empty((0, 3)), np.empty((0, 1)))"},
    {"name": "empty series", "call": "make_windows([], 2, 1)", "expected": "(np.empty((0, 2)), np.empty((0, 1)))"},
    {"name": "window 1", "call": "make_windows([5, 6, 7, 8], 1, 1)",
     "expected": "(np.array([[5], [6], [7]], dtype=float), np.array([[6], [7], [8]], dtype=float))"},
    {"name": "row count", "call": "make_windows(BIG, 24, 12)[0].shape", "expected": "(965, 24)"},
    {"name": "large with stride", "call": "make_windows(BIG, 30, 7, 5)"},
]
