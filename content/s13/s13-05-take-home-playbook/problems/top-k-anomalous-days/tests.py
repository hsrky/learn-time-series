import numpy as np
import pandas as pd

idx = pd.date_range("2024-01-01", periods=21, freq="D")   # starts on a Monday
base = [10, 10, 10, 10, 10, 20, 20] * 3
S1 = pd.Series(base, index=idx, dtype=float)
S1.iloc[9] = 50.0                                          # 2024-01-10, a Wednesday
S2 = S1.copy(); S2.iloc[16] = 5.0                          # 2024-01-17, a Wednesday dip
S3 = pd.Series([3.0, 4.0], index=pd.date_range("2024-02-01", periods=2))
S4 = pd.Series([], dtype=float, index=pd.DatetimeIndex([]))
rng = np.random.default_rng(31)
idx5 = pd.date_range("2023-01-01", periods=364, freq="D")
S5 = pd.Series(50 + 10 * np.sin(2 * np.pi * idx5.dayofweek / 7) + rng.normal(0, 2, 364), index=idx5)
S5.iloc[[40, 200, 300]] += [30, -25, 18]
S6 = pd.Series([5.0] * 14, index=pd.date_range("2024-03-04", periods=14))   # constant: all ties

CASES = [
    {"name": "one spike", "call": "top_anomalous_days(S1, 1)", "expected": "['2024-01-10']", "visible": True},
    {"name": "spike and dip", "call": "top_anomalous_days(S2, 2)", "expected": "['2024-01-10', '2024-01-17']", "visible": True},
    {"name": "fewer days than k", "call": "top_anomalous_days(S3, 5)"},
    {"name": "empty", "call": "top_anomalous_days(S4, 3)", "expected": "[]"},
    {"name": "all ties choose earliest", "call": "top_anomalous_days(S6, 3)", "expected": "['2024-03-04', '2024-03-05', '2024-03-06']"},
    {"name": "larger random", "call": "top_anomalous_days(S5, 3)"},
]
