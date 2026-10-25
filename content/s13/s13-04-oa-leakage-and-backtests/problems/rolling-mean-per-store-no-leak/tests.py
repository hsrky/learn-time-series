import numpy as np
import pandas as pd

DF1 = pd.DataFrame({"store": ["A", "A", "A", "B"],
                    "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-01"]),
                    "sales": [10, 20, 60, 5]})
DF2 = pd.DataFrame({"store": ["A", "B", "A", "B", "A", "B"],
                    "date": pd.to_datetime(["2024-02-03", "2024-02-02", "2024-02-01", "2024-02-01", "2024-02-02", "2024-02-03"]),
                    "sales": [30, 4, 10, 2, 20, 6]}, index=[10, 11, 12, 13, 14, 15])
DF3 = pd.DataFrame({"store": [], "date": pd.to_datetime([]), "sales": []})
rng = np.random.default_rng(3)
rows = [(f"s{k}", d, int(rng.integers(0, 100))) for k in range(6) for d in pd.date_range("2024-01-01", periods=60)]
DF4 = pd.DataFrame(rows, columns=["store", "date", "sales"]).sample(frac=1.0, random_state=4)

CASES = [
    {"name": "example", "call": "prev_rolling_mean(DF1, 2)", "expected": "pd.Series([np.nan, 10.0, 15.0, np.nan])", "visible": True},
    {"name": "unsorted, custom index", "call": "prev_rolling_mean(DF2, 2)",
     "expected": "pd.Series([15.0, 2.0, np.nan, np.nan, 10.0, 3.0], index=[10, 11, 12, 13, 14, 15])", "visible": True},
    {"name": "window 1 is the previous day", "call": "prev_rolling_mean(DF1, 1)", "expected": "pd.Series([np.nan, 10.0, 20.0, np.nan])"},
    {"name": "large window, short history", "call": "prev_rolling_mean(DF1, 30)", "expected": "pd.Series([np.nan, 10.0, 15.0, np.nan])"},
    {"name": "empty", "call": "prev_rolling_mean(DF3, 3)", "check_index": False},
    {"name": "larger random", "call": "prev_rolling_mean(DF4, 7)"},
]
