import numpy as np
import pandas as pd

def mk(v):
    return pd.Series(v, index=pd.date_range("2024-01-01", periods=len(v), freq="D"))

rng = np.random.default_rng(6)
BIG = mk(rng.uniform(5, 50, 1000))

CASES = [
    {"name": "example", "call": "lag_table(mk([10, 20, 40, 40]))", "visible": True},
    {"name": "five days", "call": "lag_table(mk([5.0, 4.0, 6.0, 8.0, 7.0]))",
     "expected": "pd.DataFrame({'sales': [5.0, 4.0, 6.0, 8.0, 7.0], 'lag1': [np.nan, 5.0, 4.0, 6.0, 8.0], 'change': [np.nan, -1.0, 2.0, 2.0, -1.0], 'growth': [np.nan, -0.2, 0.5, 1/3, -0.125], 'avg3_before': [np.nan, np.nan, np.nan, 5.0, 6.0]}, index=mk([0]*5).index)", "visible": True},
    {"name": "single value", "call": "lag_table(mk([3.0]))"},
    {"name": "two values", "call": "lag_table(mk([3.0, 6.0]))"},
    {"name": "columns order", "call": "list(lag_table(mk([1, 2, 3, 4])).columns)", "expected": "['sales', 'lag1', 'change', 'growth', 'avg3_before']"},
    {"name": "random 1000", "call": "lag_table(BIG)"},
]
