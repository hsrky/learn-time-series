import numpy as np
import pandas as pd

idx = pd.date_range("2024-01-01", periods=48, freq="h")
S1 = pd.Series(np.arange(48, dtype=float), index=idx)

CASES = [
    {"name": "two full days", "call": "daily_total(S1)", "visible": True},
    {"name": "one day", "call": "daily_total(S1.iloc[:24])", "expected": "pd.Series([276.0], index=pd.DatetimeIndex(['2024-01-01'], freq='D'))", "visible": True},
    {"name": "with NaN", "call": "daily_total(S1.where(S1 % 5 != 0))"},
    {"name": "partial day", "call": "daily_total(S1.iloc[:30])"},
    {"name": "random", "call": "daily_total(pd.Series(np.random.default_rng(1).normal(size=96), index=pd.date_range('2024-03-01', periods=96, freq='h')))"},
]
