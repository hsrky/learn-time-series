import numpy as np
import pandas as pd

idx = pd.date_range("2024-01-01", periods=48, freq="h")
ONES = pd.Series(1.0, index=idx)
rng = np.random.default_rng(1)
BIGI = pd.date_range("2023-01-01", periods=24 * 90, freq="h")
BIG = pd.Series(rng.uniform(0, 5, len(BIGI)), index=BIGI)
BIG[rng.random(len(BIG)) < 0.1] = np.nan
GAP = ONES.drop(ONES.index[24:48].union(ONES.index[0:0]))
THREE = pd.Series(1.0, index=pd.date_range("2024-01-01", periods=72, freq="h"))
THREE = THREE.drop(THREE.index[24:48])

CASES = [
    {"name": "two full days", "call": "daily_totals(ONES)", "expected": "pd.Series([24.0, 24.0], index=pd.date_range('2024-01-01', periods=2, freq='D'))", "visible": True},
    {"name": "partial day", "call": "daily_totals(ONES.iloc[:30])", "expected": "pd.Series([24.0, 6.0], index=pd.date_range('2024-01-01', periods=2, freq='D'))", "visible": True},
    {"name": "NaN hours count as 0", "call": "daily_totals(ONES.where(ONES.index.hour % 2 == 0))", "expected": "pd.Series([12.0, 12.0], index=pd.date_range('2024-01-01', periods=2, freq='D'))"},
    {"name": "a whole day missing in the middle", "call": "daily_totals(THREE)", "expected": "pd.Series([24.0, 0.0, 24.0], index=pd.date_range('2024-01-01', periods=3, freq='D'))"},
    {"name": "single value", "call": "daily_totals(ONES.iloc[:1])", "expected": "pd.Series([1.0], index=pd.date_range('2024-01-01', periods=1, freq='D'))"},
    {"name": "random 90 days with NaN", "call": "daily_totals(BIG)"},
]
