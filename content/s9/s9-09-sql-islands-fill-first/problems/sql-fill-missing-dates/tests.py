import numpy as np
import pandas as pd
DAILY_GAPS = pd.DataFrame({"day": ["2024-01-01", "2024-01-02", "2024-01-05"], "revenue": [10.0, 20.0, 50.0]})
rng = np.random.default_rng(34)
_all = pd.date_range("2023-06-01", periods=700, freq="D")
_keep = _all[rng.random(700) < 0.6]
BIG = pd.DataFrame({"day": _keep.strftime("%Y-%m-%d"), "revenue": np.round(rng.uniform(1, 50, len(_keep)), 2)}).sample(frac=1, random_state=3)
CASES = [
    {"name": "gap of two days", "call": "sql(QUERY, daily=DAILY_GAPS)", "visible": True},
    {"name": "no gaps", "call": "sql(QUERY, daily=DAILY_GAPS.iloc[:2])", "visible": True},
    {"name": "one row", "call": "sql(QUERY, daily=DAILY_GAPS.iloc[:1])"},
    {"name": "across a leap day", "call": "sql(QUERY, daily=pd.DataFrame({'day': ['2024-02-27', '2024-03-02'], 'revenue': [5.0, 6.0]}))"},
    {"name": "across a year end, unsorted", "call": "sql(QUERY, daily=pd.DataFrame({'day': ['2024-01-02', '2023-12-30'], 'revenue': [1.0, 2.0]}))"},
    {"name": "random larger case", "call": "sql(QUERY, daily=BIG)"},
]
