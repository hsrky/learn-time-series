import numpy as np
import pandas as pd

A = pd.DataFrame({"series_id": "a", "date": pd.date_range("2024-01-01", periods=5, freq="D"),
                  "y": [10.0, 12.0, 11.0, 13.0, 15.0]})
B = pd.DataFrame({"series_id": "b", "date": pd.date_range("2024-01-01", periods=9, freq="D"),
                  "y": np.arange(9.0) ** 2})
TWO = pd.concat([A, B]).sample(frac=1.0, random_state=3)
GAP = pd.DataFrame({"series_id": "g", "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-05", "2024-01-06"]),
                    "y": [1.0, 2.0, 4.0, 8.0]})
rng = np.random.default_rng(8)
rows = []
for sid in ["s1", "s2", "s3", "s4"]:
    d = pd.date_range("2023-01-01", periods=60, freq="D")
    rows.append(pd.DataFrame({"series_id": sid, "date": d, "y": rng.gamma(2.0, 10.0, 60)}))
BIG = pd.concat(rows).sample(frac=1.0, random_state=5)

CASES = [
    {"name": "one series", "call": "build_features(A)", "visible": True},
    {"name": "two shuffled series", "call": "build_features(TWO)", "visible": True},
    {"name": "features ignore gaps in dates (row based)", "call": "build_features(GAP)", "visible": True},
    {"name": "lags do not cross series", "call": "build_features(TWO).groupby('series_id')['lag_1'].apply(lambda s: bool(pd.isna(s.iloc[0]))).tolist()",
     "expected": "[True, True]"},
    {"name": "last row does not use its own y", "call": "build_features(A).iloc[-1][['lag_1', 'roll_mean_3', 'exp_mean']].tolist()",
     "expected": "[13.0, 12.0, 11.5]"},
    {"name": "empty table", "call": "build_features(A.iloc[0:0]).shape", "expected": "(0, 8)"},
    {"name": "changing the last y changes no feature of that row", "call": "build_features(A.assign(y=[10.0, 12.0, 11.0, 13.0, 999.0])).iloc[-1][['lag_1', 'lag_7', 'roll_mean_3', 'roll_std_3', 'exp_mean']].tolist()",
     "expected": "[13.0, float('nan'), 12.0, 1.0, 11.5]"},
    {"name": "large random panel", "call": "build_features(BIG)"},
]
