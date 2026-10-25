import numpy as np
import pandas as pd

idx = pd.date_range("2024-01-01", periods=14, freq="D")
S = pd.Series([1, 2, 3, 4, 5, 6, 7, 3, 4, 5, 6, 7, 8, 9], index=idx, dtype=float)
rng = np.random.default_rng(8)
BIG = pd.Series(rng.normal(100, 20, 400), index=pd.date_range("2023-01-01", periods=400, freq="D"))
BIG[::13] = np.nan

CASES = [
    {"name": "two weeks", "call": "weekday_profile(S)", "expected": "pd.Series([2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0], index=range(7))", "visible": True},
    {"name": "three days only", "call": "weekday_profile(S.iloc[:3])", "expected": "pd.Series([1.0, 2.0, 3.0, np.nan, np.nan, np.nan, np.nan], index=range(7))", "visible": True},
    {"name": "start on Wednesday", "call": "weekday_profile(pd.Series([10.0, 20.0], index=pd.to_datetime(['2024-01-03', '2024-01-04'])))", "expected": "pd.Series([np.nan, np.nan, 10.0, 20.0, np.nan, np.nan, np.nan], index=range(7))"},
    {"name": "NaN skipped", "call": "weekday_profile(S.where(S != 3))", "expected": "pd.Series([1.0, 3.0, 5.0, 5.0, 6.0, 7.0, 8.0], index=range(7))"},
    {"name": "single value", "call": "weekday_profile(S.iloc[:1])", "expected": "pd.Series([1.0] + [np.nan] * 6, index=range(7))"},
    {"name": "random 400 days", "call": "weekday_profile(BIG)"},
]
