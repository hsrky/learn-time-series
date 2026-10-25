import numpy as np
import pandas as pd

def mk(v):
    return pd.Series(v, index=pd.date_range("2024-01-01", periods=len(v), freq="D"), dtype=float)

rng = np.random.default_rng(17)
BIG = mk(100 * np.exp(rng.normal(0, 0.02, 2000).cumsum()))

CASES = [
    {"name": "example", "call": "log_returns(mk([100, 110, 99]))", "visible": True},
    {"name": "flat price", "call": "log_returns(mk([5, 5, 5]))", "expected": "mk([np.nan, 0.0, 0.0])", "visible": True},
    {"name": "single price", "call": "log_returns(mk([42]))", "expected": "mk([np.nan])"},
    {"name": "doubling", "call": "log_returns(mk([1, 2, 4]))", "expected": "mk([np.nan, math.log(2), math.log(2)])"},
    {"name": "sum equals total", "call": "float(log_returns(mk([100, 120, 90, 150])).sum())", "expected": "math.log(150 / 100)"},
    {"name": "random 2000", "call": "log_returns(BIG)"},
]
