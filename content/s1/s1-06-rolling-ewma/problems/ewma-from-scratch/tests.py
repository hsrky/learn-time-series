import numpy as np
import pandas as pd

rng = np.random.default_rng(23)
BIG = rng.normal(50, 10, 3000)
BIGN = BIG.copy()
BIGN[rng.random(3000) < 0.1] = np.nan

CASES = [
    {"name": "example 1", "call": "ewma([10, 10, 20], 0.4)", "expected": "np.array([10.0, 10.0, 14.0])", "visible": True},
    {"name": "example 2 with nan", "call": "ewma([1, np.nan, 3], 0.5)", "expected": "np.array([1.0, 1.0, 2.0])", "visible": True},
    {"name": "alpha 1 copies", "call": "ewma([3, 5, 7], 1.0)", "expected": "np.array([3.0, 5.0, 7.0])"},
    {"name": "leading nan", "call": "ewma([np.nan, np.nan, 4, 8], 0.5)", "expected": "np.array([np.nan, np.nan, 4.0, 6.0])"},
    {"name": "empty", "call": "ewma([], 0.5)", "expected": "np.array([])"},
    {"name": "single", "call": "ewma([7], 0.2)", "expected": "np.array([7.0])"},
    {"name": "matches pandas (no nan)", "call": "ewma(BIG, 0.1)", "expected": "pd.Series(BIG).ewm(alpha=0.1, adjust=False).mean().to_numpy()"},
    {"name": "random 3000 with nan", "call": "ewma(BIGN, 0.3)"},
]
