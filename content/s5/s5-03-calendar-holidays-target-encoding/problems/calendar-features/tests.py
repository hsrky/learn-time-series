import numpy as np
import pandas as pd

D1 = pd.date_range("2024-12-23", periods=5, freq="D")
D2 = pd.DatetimeIndex(["2024-03-05", "2024-01-01", "2024-02-29", "2024-12-31"])
rng = np.random.default_rng(4)
BIGD = pd.DatetimeIndex(pd.date_range("2020-01-01", "2024-12-31", freq="D")[rng.permutation(1827)[:800]])
HOL = ["2020-12-25", "2021-12-25", "2022-12-25", "2023-12-25", "2024-12-25", "2022-01-01", "2024-07-04", "2024-07-04"]

CASES = [
    {"name": "one holiday", "call": "calendar_features(D1, ['2024-12-25'])", "visible": True,
     "expected": "pd.DataFrame({'dow': [0,1,2,3,4], 'is_weekend': [0,0,0,0,0], 'month': [12]*5, 'is_holiday': [0,0,1,0,0], 'days_to_next': [2,1,0,np.nan,np.nan], 'days_since_last': [np.nan,np.nan,0,1,2]}, index=D1)"},
    {"name": "unsorted dates, two holidays", "call": "calendar_features(D2, ['2024-02-01', '2024-01-01'])", "visible": True},
    {"name": "no holidays", "call": "calendar_features(D1, [])", "visible": True,
     "expected": "pd.DataFrame({'dow': [0,1,2,3,4], 'is_weekend': [0,0,0,0,0], 'month': [12]*5, 'is_holiday': [0]*5, 'days_to_next': [np.nan]*5, 'days_since_last': [np.nan]*5}, index=D1)"},
    {"name": "weekend flag", "call": "calendar_features(pd.DatetimeIndex(['2024-06-01', '2024-06-02', '2024-06-03']), ['2024-06-02'])['is_weekend'].tolist()",
     "expected": "[1, 1, 0]"},
    {"name": "empty dates", "call": "calendar_features(pd.DatetimeIndex([]), ['2024-01-01']).shape", "expected": "(0, 6)"},
    {"name": "duplicate holidays", "call": "calendar_features(D1, ['2024-12-25', '2024-12-25'])"},
    {"name": "large shuffled index", "call": "calendar_features(BIGD, HOL)"},
]
