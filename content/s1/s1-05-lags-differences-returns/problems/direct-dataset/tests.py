import numpy as np
import pandas as pd

def mk(v):
    return pd.Series(v, index=pd.date_range("2024-01-01", periods=len(v), freq="D"), dtype=float)

rng = np.random.default_rng(19)
BIG = mk(rng.normal(0, 1, 1500).cumsum())
IDX = pd.date_range("2024-01-01", periods=5, freq="D")

CASES = [
    {"name": "example", "call": "direct_dataset(mk([1, 2, 3, 4, 5]), 2, 1)",
     "expected": "pd.DataFrame({'lag_0': [2.0, 3.0, 4.0], 'lag_1': [1.0, 2.0, 3.0], 'target': [3.0, 4.0, 5.0]}, index=IDX[1:4])", "visible": True},
    {"name": "horizon 3", "call": "direct_dataset(mk([1, 2, 3, 4, 5]), 1, 3)",
     "expected": "pd.DataFrame({'lag_0': [1.0, 2.0], 'target': [4.0, 5.0]}, index=IDX[0:2])", "visible": True},
    {"name": "too short gives empty", "call": "len(direct_dataset(mk([1, 2]), 3, 1))", "expected": "0"},
    {"name": "column names and order", "call": "list(direct_dataset(mk(list(range(10))), 3, 2).columns)", "expected": "['lag_0', 'lag_1', 'lag_2', 'target']"},
    {"name": "last target is the last value, first lag_3 is the first value", "call": "d = direct_dataset(BIG, 4, 5)\n(float(d['target'].iloc[-1]) == float(BIG.iloc[-1]), float(d['lag_3'].iloc[0]) == float(BIG.iloc[0]), len(d))", "expected": "(True, True, 1492)"},
    {"name": "random 1500 h=7 lags=10", "call": "direct_dataset(BIG, 10, 7)"},
]
