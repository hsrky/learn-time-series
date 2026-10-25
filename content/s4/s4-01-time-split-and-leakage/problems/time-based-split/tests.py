import numpy as np
import pandas as pd

idx = pd.date_range("2024-01-01", periods=10, freq="D")
D = pd.DataFrame({"a": np.arange(10.0), "b": np.arange(10.0) * 2}, index=idx)
SHUF = D.iloc[[7, 2, 9, 0, 5, 1, 8, 3, 6, 4]]
rng = np.random.default_rng(42)
BIG_IDX = pd.date_range("2020-01-01", periods=500, freq="D")
BIG = pd.DataFrame({"x": rng.normal(size=500)}, index=BIG_IDX).sample(frac=1.0, random_state=1)

CASES = [
    {"name": "no gap", "call": "time_split(D, '2024-01-08')", "visible": True,
     "expected": "(D.iloc[:7], D.iloc[7:])"},
    {"name": "gap of 2 days", "call": "time_split(D, '2024-01-08', gap_days=2)", "visible": True,
     "expected": "(D.iloc[:5], D.iloc[7:])"},
    {"name": "unsorted input", "call": "time_split(SHUF, pd.Timestamp('2024-01-04'))", "visible": True,
     "expected": "(D.iloc[:3], D.iloc[3:])"},
    {"name": "cutoff after all data", "call": "time_split(D, '2025-01-01')",
     "expected": "(D, D.iloc[0:0])"},
    {"name": "cutoff before all data", "call": "time_split(D, '2023-01-01', gap_days=5)",
     "expected": "(D.iloc[0:0], D)"},
    {"name": "gap larger than history", "call": "time_split(D, '2024-01-03', gap_days=30)",
     "expected": "(D.iloc[0:0], D.iloc[2:])"},
    {"name": "empty frame", "call": "time_split(D.iloc[0:0], '2024-01-03')",
     "expected": "(D.iloc[0:0], D.iloc[0:0])"},
    {"name": "large shuffled case", "call": "time_split(BIG, '2021-03-01', gap_days=7)"},
]
