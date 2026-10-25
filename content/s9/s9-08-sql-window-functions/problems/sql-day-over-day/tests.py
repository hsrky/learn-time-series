import numpy as np
import pandas as pd
DAILY_SMALL = pd.DataFrame({"day": ["2024-01-01", "2024-01-02", "2024-01-03"], "revenue": [100.0, 130.0, 120.0]})
_days = pd.date_range("2024-01-01", periods=400, freq="D").strftime("%Y-%m-%d")
rng = np.random.default_rng(30)
DAILY_BIG = pd.DataFrame({"day": _days, "revenue": np.round(rng.normal(1000, 100, 400), 2)}).sample(frac=1, random_state=1)
CASES = [
    {"name": "three days", "call": "sql(QUERY, daily=DAILY_SMALL)", "visible": True},
    {"name": "single day", "call": "sql(QUERY, daily=DAILY_SMALL.iloc[:1])", "visible": True, "check_index": False},
    {"name": "unsorted table", "call": "sql(QUERY, daily=DAILY_SMALL.iloc[::-1])", "check_index": False},
    {"name": "crosses a month end", "call": "sql(QUERY, daily=pd.DataFrame({'day': ['2024-01-31', '2024-02-01', '2024-02-02'], 'revenue': [5.0, 7.0, 4.0]}))", "check_index": False},
    {"name": "random larger case, shuffled rows", "call": "sql(QUERY, daily=DAILY_BIG)", "check_index": False},
]
