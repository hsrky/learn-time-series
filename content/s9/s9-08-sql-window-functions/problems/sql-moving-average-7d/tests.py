import numpy as np
import pandas as pd
DAILY_8 = pd.DataFrame({"day": pd.date_range("2024-03-01", periods=8, freq="D").strftime("%Y-%m-%d"), "revenue": [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 150.0]})
rng = np.random.default_rng(31)
DAILY_BIG = pd.DataFrame({"day": pd.date_range("2023-01-01", periods=500, freq="D").strftime("%Y-%m-%d"), "revenue": np.round(rng.normal(300, 40, 500), 2)}).sample(frac=1, random_state=2)
CASES = [
    {"name": "eight days", "call": "sql(QUERY, daily=DAILY_8)", "visible": True},
    {"name": "fewer than 7 days", "call": "sql(QUERY, daily=DAILY_8.iloc[:4])", "visible": True},
    {"name": "exactly 7 days", "call": "sql(QUERY, daily=DAILY_8.iloc[:7])"},
    {"name": "constant revenue", "call": "sql(QUERY, daily=DAILY_8.assign(revenue=5.0))"},
    {"name": "shuffled input rows", "call": "sql(QUERY, daily=DAILY_8.sample(frac=1, random_state=0))"},
    {"name": "random larger case", "call": "sql(QUERY, daily=DAILY_BIG)"},
]
