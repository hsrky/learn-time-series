import numpy as np
import pandas as pd

def mk(d):
    return pd.Series(list(d.values()), index=pd.to_datetime(list(d.keys())), dtype=float)

S1 = mk({"2024-01-01": 10, "2024-01-02": -999, "2024-01-05": 14, "2024-01-06": 15})
rng = np.random.default_rng(31)
days = pd.date_range("2023-01-01", periods=500, freq="D")
keep = days[rng.random(500) > 0.15]
vals = rng.normal(15, 5, len(keep)).round(1)
vals[rng.random(len(keep)) < 0.1] = -999
BIG = pd.Series(vals, index=keep)

def D(start, n):
    return pd.date_range(start, periods=n, freq="D")

CASES = [
    {"name": "example", "call": "causal_fill(S1, 1)", "expected": "pd.Series([10.0, 10.0, np.nan, np.nan, 14.0, 15.0], index=D('2024-01-01', 6))", "visible": True},
    {"name": "bigger gap allowed", "call": "causal_fill(S1, 5)", "expected": "pd.Series([10.0, 10.0, 10.0, 10.0, 14.0, 15.0], index=D('2024-01-01', 6))", "visible": True},
    {"name": "max_gap zero", "call": "causal_fill(S1, 0)", "expected": "pd.Series([10.0, np.nan, np.nan, np.nan, 14.0, 15.0], index=D('2024-01-01', 6))"},
    {"name": "no gaps", "call": "causal_fill(mk({'2024-01-01': 1, '2024-01-02': 2}), 3)", "expected": "pd.Series([1.0, 2.0], index=D('2024-01-01', 2))"},
    {"name": "leading gap stays NaN", "call": "causal_fill(mk({'2024-01-01': -999, '2024-01-02': 5}), 3)", "expected": "pd.Series([np.nan, 5.0], index=D('2024-01-01', 2))"},
    {"name": "never uses the future", "call": "causal_fill(mk({'2024-01-01': 1, '2024-01-04': 100}), 2).iloc[:3]", "expected": "pd.Series([1.0, 1.0, 1.0], index=D('2024-01-01', 3))"},
    {"name": "random 500 days", "call": "causal_fill(BIG, 3)"},
]
