import numpy as np
import pandas as pd

S1 = pd.Series([10, 20, 30, 40, 12, 22, 32, 42])
S2 = pd.Series([1, 4, 9, 16, 25])
idx = pd.date_range("2024-01-01", periods=60, freq="D")
rng = np.random.default_rng(7)
S3 = pd.Series(0.5 * np.arange(60) + 3 * np.sin(2 * np.pi * np.arange(60) / 7) + rng.normal(0, 0.1, 60), index=idx)

CASES = [
    {"name": "seasonal only", "call": "difference(S1, m=4)", "visible": True},
    {"name": "second difference", "call": "difference(S2, d=2)", "visible": True},
    {"name": "nothing to do", "call": "difference(S2)"},
    {"name": "seasonal then regular", "call": "difference(S1, m=4, d=1)"},
    {"name": "too short returns empty", "call": "difference(S2, m=2, d=3)", "expected": "pd.Series([], dtype=float)"},
    {"name": "daily weekly season, date index", "call": "difference(S3, m=7, d=1)"},
    {"name": "weekly season removed (small spread left)", "call": "round(float(difference(S3, m=7).std()), 1)"},
]
