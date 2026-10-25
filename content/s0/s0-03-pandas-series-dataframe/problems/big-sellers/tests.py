import numpy as np
import pandas as pd

idx = pd.date_range("2024-01-01", periods=3, freq="D")
D1 = pd.DataFrame({"units": [10, 30, 60]}, index=idx)
D2 = pd.DataFrame({"units": [5, 5], "store": ["A", "B"]}, index=idx[:2])
rng = np.random.default_rng(9)
BIG = pd.DataFrame({"units": rng.integers(0, 100, 1000), "store": rng.choice(list("ABC"), 1000)},
                   index=pd.date_range("2023-01-01", periods=1000, freq="D"))

CASES = [
    {"name": "basic", "call": "big_sellers(D1, 0.3)", "expected": "pd.DataFrame({'units': [30, 60], 'share': [0.3, 0.6]}, index=idx[1:])", "visible": True},
    {"name": "keep all", "call": "big_sellers(D1, 0.0)", "expected": "pd.DataFrame({'units': [10, 30, 60], 'share': [0.1, 0.3, 0.6]}, index=idx)", "visible": True},
    {"name": "other columns stay", "call": "big_sellers(D2, 0.5)", "expected": "pd.DataFrame({'units': [5, 5], 'store': ['A', 'B'], 'share': [0.5, 0.5]}, index=idx[:2])"},
    {"name": "nothing kept", "call": "big_sellers(D1, 0.9)", "expected": "pd.DataFrame({'units': pd.Series([], dtype='int64'), 'share': pd.Series([], dtype='float64')}, index=idx[:0])"},
    {"name": "input unchanged", "call": "big_sellers(D1, 0.3)\nlist(D1.columns)", "expected": "['units']"},
    {"name": "random 1000 rows", "call": "big_sellers(BIG, 0.001)"},
]
