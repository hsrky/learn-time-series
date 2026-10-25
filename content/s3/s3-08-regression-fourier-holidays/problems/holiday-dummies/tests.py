import numpy as np
import pandas as pd

D1 = pd.date_range("2023-12-23", periods=5, freq="D")
D2 = pd.date_range("2024-01-01", periods=3, freq="D")
D_HOURLY = pd.date_range("2024-03-01 06:00", periods=5, freq="12h")
D_YEAR = pd.date_range("2022-01-01", periods=3 * 365, freq="D")
D_SHUF = pd.DatetimeIndex(["2024-01-03", "2024-01-01", "2024-01-02"])
HOL = {"xmas": ["2022-12-25", "2023-12-25", "2024-12-25"], "ny": ["2022-01-01", "2023-01-01"]}

CASES = [
    {"name": "day before and Christmas", "call": "holiday_features(D1, {'xmas': ['2023-12-25']}, before=1)", "visible": True},
    {"name": "two holidays", "call": "holiday_features(D2, {'a': ['2024-01-01'], 'b': ['2024-01-02']})", "visible": True},
    {"name": "holiday outside the range", "call": "holiday_features(D1, {'x': ['2030-01-01']})"},
    {"name": "time of day is ignored", "call": "holiday_features(D_HOURLY, {'h': ['2024-03-02']})"},
    {"name": "unsorted dates keep their order", "call": "holiday_features(D_SHUF, {'h': ['2024-01-02']}, after=1)"},
    {"name": "no holidays", "call": "holiday_features(D2, {})"},
    {"name": "three years, windows", "call": "holiday_features(D_YEAR, HOL, before=2, after=1)"},
    {"name": "count of marked days", "call": "int(holiday_features(D_YEAR, HOL, before=2, after=1)['any_holiday'].sum())"},
]
