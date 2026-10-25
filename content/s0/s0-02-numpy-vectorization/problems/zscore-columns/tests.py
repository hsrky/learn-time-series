import numpy as np

rng = np.random.default_rng(5)
BIG = rng.normal(50, 10, size=(500, 8))
BIG[rng.random(BIG.shape) < 0.1] = np.nan

CASES = [
    {"name": "constant column", "call": "zscore_columns(np.array([[1.0, 5.0], [3.0, 5.0]]))", "expected": "np.array([[-1.0, 0.0], [1.0, 0.0]])", "visible": True},
    {"name": "with nan", "call": "zscore_columns(np.array([[1.0, 2.0], [np.nan, 4.0], [3.0, 6.0]]))", "visible": True},
    {"name": "single column", "call": "zscore_columns(np.array([[2.0], [4.0], [6.0], [8.0]]))"},
    {"name": "single row", "call": "zscore_columns(np.array([[1.0, 2.0, 3.0]]))", "expected": "np.zeros((1, 3))"},
    {"name": "random 500x8 with nan", "call": "zscore_columns(BIG)"},
]
