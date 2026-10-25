import numpy as np
import pandas as pd

O1 = pd.DataFrame({"date": pd.to_datetime(["2024-01-05", "2024-01-08"]), "dcoilwtico": [70.0, 72.0]})
O2 = pd.DataFrame({"date": pd.to_datetime(["2024-01-10", "2024-01-08", "2024-01-09", "2024-01-12"]),
                   "dcoilwtico": [75.0, np.nan, 74.0, np.nan]})
O3 = pd.DataFrame({"date": pd.to_datetime([]), "dcoilwtico": pd.Series([], dtype=float)})
O4 = pd.DataFrame({"date": pd.to_datetime(["2024-01-02"]), "dcoilwtico": [np.nan]})
rng = np.random.default_rng(10)
bd = pd.bdate_range("2023-01-02", "2023-12-29")
O5 = pd.DataFrame({"date": bd, "dcoilwtico": 60 + np.cumsum(rng.normal(0, 1, len(bd)))})
O5.loc[rng.choice(len(bd), 15, replace=False), "dcoilwtico"] = np.nan
O5 = O5.sample(frac=1.0, random_state=3)

CASES = [
    {"name": "weekend and after last price", "call": "daily_oil(O1, '2024-01-05', '2024-01-09')", "visible": True,
     "expected": "pd.DataFrame({'date': pd.date_range('2024-01-05', '2024-01-09'), 'dcoilwtico': [70.0, 70.0, 70.0, 72.0, 72.0]})"},
    {"name": "NaN prices and backward fill at the start", "call": "daily_oil(O2, '2024-01-06', '2024-01-12')", "visible": True,
     "expected": "pd.DataFrame({'date': pd.date_range('2024-01-06', '2024-01-12'), 'dcoilwtico': [74.0, 74.0, 74.0, 74.0, 75.0, 75.0, 75.0]})"},
    {"name": "start after the first known price", "call": "daily_oil(O1, '2024-01-06', '2024-01-07')",
     "expected": "pd.DataFrame({'date': pd.date_range('2024-01-06', '2024-01-07'), 'dcoilwtico': [70.0, 70.0]})"},
    {"name": "no data at all", "call": "daily_oil(O3, '2024-01-01', '2024-01-03')",
     "expected": "pd.DataFrame({'date': pd.date_range('2024-01-01', '2024-01-03'), 'dcoilwtico': [np.nan] * 3})"},
    {"name": "only NaN", "call": "daily_oil(O4, '2024-01-01', '2024-01-03')",
     "expected": "pd.DataFrame({'date': pd.date_range('2024-01-01', '2024-01-03'), 'dcoilwtico': [np.nan] * 3})"},
    {"name": "larger random, shuffled", "call": "daily_oil(O5, '2023-01-01', '2024-01-10')"},
]
