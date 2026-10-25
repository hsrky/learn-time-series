import numpy as np
import pandas as pd

T = pd.to_datetime(["2024-01-01 00:00", "2024-01-01 01:00", "2024-01-01 04:00"])
S1 = pd.Series([10.0, np.nan, 16.0], index=T)
rng = np.random.default_rng(15)
secs = np.sort(rng.choice(100000, 600, replace=False))
BIG = pd.Series(rng.normal(0, 1, 600).cumsum(), index=pd.Timestamp("2024-01-01") + pd.to_timedelta(secs, unit="s"))
BIG[rng.random(600) < 0.3] = np.nan

CASES = [
    {"name": "uneven spacing", "call": "interpolate_by_time(S1)", "expected": "pd.Series([10.0, 11.5, 16.0], index=T)", "visible": True},
    {"name": "even spacing", "call": "interpolate_by_time(pd.Series([0.0, np.nan, np.nan, 6.0], index=pd.date_range('2024-01-01', periods=4, freq='D')))", "expected": "pd.Series([0.0, 2.0, 4.0, 6.0], index=pd.date_range('2024-01-01', periods=4, freq='D'))", "visible": True},
    {"name": "edges stay NaN", "call": "interpolate_by_time(pd.Series([np.nan, 2.0, np.nan, 4.0, np.nan], index=pd.date_range('2024-01-01', periods=5, freq='D')))", "expected": "pd.Series([np.nan, 2.0, 3.0, 4.0, np.nan], index=pd.date_range('2024-01-01', periods=5, freq='D'))"},
    {"name": "all NaN", "call": "interpolate_by_time(pd.Series([np.nan, np.nan], index=pd.date_range('2024-01-01', periods=2, freq='D')))", "expected": "pd.Series([np.nan, np.nan], index=pd.date_range('2024-01-01', periods=2, freq='D'))"},
    {"name": "no NaN", "call": "interpolate_by_time(pd.Series([1.0, 2.0], index=pd.date_range('2024-01-01', periods=2, freq='D')))", "expected": "pd.Series([1.0, 2.0], index=pd.date_range('2024-01-01', periods=2, freq='D'))"},
    {"name": "same as pandas time method", "call": "interpolate_by_time(BIG)", "expected": "BIG.interpolate(method='time', limit_area='inside')"},
]
