import numpy as np
import pandas as pd

def mk(v):
    return pd.Series(v, index=pd.date_range("2024-01-01", periods=len(v), freq="D"), dtype=float)

rng = np.random.default_rng(29)
vals = rng.normal(100, 5, 1000)
vals[[100, 400, 700]] += 60
BIG = mk(vals)

CASES = [
    {"name": "example", "call": "rolling_zscore(mk([10, 12, 14, 30]), 3)", "expected": "mk([np.nan, np.nan, np.nan, 9.0])", "visible": True},
    {"name": "window 2", "call": "rolling_zscore(mk([1, 3, 5, 9]), 2)", "expected": "mk([np.nan, np.nan, 3 / math.sqrt(2), 5 / math.sqrt(2)])", "visible": True},
    {"name": "constant history gives NaN", "call": "rolling_zscore(mk([5, 5, 5, 9]), 3)", "expected": "mk([np.nan, np.nan, np.nan, np.nan])"},
    {"name": "too short", "call": "rolling_zscore(mk([1, 2]), 3)", "expected": "mk([np.nan, np.nan])"},
    {"name": "spike is detected", "call": "float(rolling_zscore(BIG, 30).iloc[100]) > 6", "expected": "True"},
    {"name": "random 1000", "call": "rolling_zscore(BIG, 30)"},
]
