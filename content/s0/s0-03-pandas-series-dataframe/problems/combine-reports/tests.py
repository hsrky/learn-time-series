import numpy as np
import pandas as pd

def mk(vals, dates):
    return pd.Series(vals, index=pd.to_datetime(dates))

A = mk([8, 9], ["2024-03-01", "2024-03-02"])
B = mk([5, 6], ["2024-03-02", "2024-03-03"])
rng = np.random.default_rng(2)
days = pd.date_range("2024-01-01", periods=300, freq="D")
BA = pd.Series(rng.integers(0, 50, 200), index=rng.permutation(days)[:200])
BB = pd.Series(rng.integers(0, 50, 220), index=rng.permutation(days)[:220])

CASES = [
    {"name": "partly overlapping", "call": "combine_reports(A, B)", "expected": "mk([8.0, 14.0, 6.0], ['2024-03-01', '2024-03-02', '2024-03-03'])", "visible": True},
    {"name": "same dates", "call": "combine_reports(A, A)", "expected": "mk([16.0, 18.0], ['2024-03-01', '2024-03-02'])", "visible": True},
    {"name": "no overlap", "call": "combine_reports(A.iloc[:1], B.iloc[1:])", "expected": "mk([8.0, 6.0], ['2024-03-01', '2024-03-03'])"},
    {"name": "unsorted input", "call": "combine_reports(mk([1, 2], ['2024-03-05', '2024-03-01']), mk([10], ['2024-03-03']))", "expected": "mk([2.0, 10.0, 1.0], ['2024-03-01', '2024-03-03', '2024-03-05'])"},
    {"name": "NaN counts as 0", "call": "combine_reports(mk([np.nan, 4.0], ['2024-03-01', '2024-03-02']), mk([1.0], ['2024-03-01']))", "expected": "mk([1.0, 4.0], ['2024-03-01', '2024-03-02'])"},
    {"name": "one empty", "call": "combine_reports(A, A.iloc[:0])", "expected": "mk([8.0, 9.0], ['2024-03-01', '2024-03-02'])"},
    {"name": "random 200 + 220 days", "call": "combine_reports(BA, BB)"},
]
