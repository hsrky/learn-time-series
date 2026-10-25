import numpy as np
import pandas as pd

rng = np.random.default_rng(12)
full = pd.date_range("2024-01-01", periods=2000, freq="h")
keep = full[rng.random(2000) > 0.2]
BIG = pd.DatetimeIndex(rng.permutation(keep))

CASES = [
    {"name": "two missing hours", "call": "missing_timestamps(pd.DatetimeIndex(['2024-01-01 00:00', '2024-01-01 01:00', '2024-01-01 04:00']), 'h')", "expected": "['2024-01-01 02:00', '2024-01-01 03:00']", "visible": True},
    {"name": "nothing missing", "call": "missing_timestamps(pd.date_range('2024-01-01', periods=5, freq='D'), 'D')", "expected": "[]", "visible": True},
    {"name": "daily gap", "call": "missing_timestamps(pd.DatetimeIndex(['2024-01-01', '2024-01-02', '2024-01-06']), 'D')", "expected": "['2024-01-03 00:00', '2024-01-04 00:00', '2024-01-05 00:00']"},
    {"name": "unsorted with duplicates", "call": "missing_timestamps(pd.DatetimeIndex(['2024-01-03', '2024-01-01', '2024-01-03', '2024-01-01']), 'D')", "expected": "['2024-01-02 00:00']"},
    {"name": "empty", "call": "missing_timestamps(pd.DatetimeIndex([]), 'D')", "expected": "[]"},
    {"name": "single time", "call": "missing_timestamps(pd.DatetimeIndex(['2024-05-05 10:00']), 'h')", "expected": "[]"},
    {"name": "15 minute grid", "call": "missing_timestamps(pd.DatetimeIndex(['2024-01-01 00:00', '2024-01-01 00:45']), '15min')", "expected": "['2024-01-01 00:15', '2024-01-01 00:30']"},
    {"name": "random 2000 hours", "call": "missing_timestamps(BIG, 'h')"},
]
