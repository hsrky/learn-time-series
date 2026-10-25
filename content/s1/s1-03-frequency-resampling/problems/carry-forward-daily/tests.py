import numpy as np
import pandas as pd

def mk(d):
    return pd.Series(list(d.values()), index=pd.to_datetime(list(d.keys())))

C1 = mk({"2024-01-01": 5.0, "2024-01-04": 6.0})
rng = np.random.default_rng(14)
days = pd.date_range("2023-01-01", "2023-12-31", freq="D")
pick = rng.permutation(days)[:40]
BIG = pd.Series(rng.uniform(1, 9, 40).round(2), index=pick)

CASES = [
    {"name": "example", "call": "daily_price(C1, '2024-01-06')", "expected": "pd.Series([5.0, 5.0, 5.0, 6.0, 6.0, 6.0], index=pd.date_range('2024-01-01', periods=6, freq='D'))", "visible": True},
    {"name": "end equals first date", "call": "daily_price(C1, '2024-01-01')", "expected": "pd.Series([5.0], index=pd.date_range('2024-01-01', periods=1, freq='D'))", "visible": True},
    {"name": "unsorted input", "call": "daily_price(mk({'2024-01-04': 6.0, '2024-01-01': 5.0}), '2024-01-05')", "expected": "pd.Series([5.0, 5.0, 5.0, 6.0, 6.0], index=pd.date_range('2024-01-01', periods=5, freq='D'))"},
    {"name": "changes after end are ignored", "call": "daily_price(C1, '2024-01-03')", "expected": "pd.Series([5.0, 5.0, 5.0], index=pd.date_range('2024-01-01', periods=3, freq='D'))"},
    {"name": "no future prices used", "call": "daily_price(mk({'2024-01-01': 1.0, '2024-01-10': 100.0}), '2024-01-09').max()", "expected": "1.0"},
    {"name": "random 40 changes", "call": "daily_price(BIG, '2023-12-31')"},
]
