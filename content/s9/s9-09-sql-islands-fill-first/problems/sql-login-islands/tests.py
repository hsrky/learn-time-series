import numpy as np
import pandas as pd
LOGINS_SMALL = pd.DataFrame({
    "user_id": ["a", "a", "a", "a", "a", "b"],
    "day": ["2024-01-01", "2024-01-02", "2024-01-02", "2024-01-03", "2024-01-05", "2024-01-10"],
})
rng = np.random.default_rng(33)
BIG = pd.DataFrame({
    "user_id": ["u%d" % i for i in rng.integers(0, 25, 3000)],
    "day": (pd.Timestamp("2023-12-15") + pd.to_timedelta(rng.integers(0, 90, 3000), unit="D")).strftime("%Y-%m-%d"),
})
CASES = [
    {"name": "small", "call": "sql(QUERY, logins=LOGINS_SMALL)", "visible": True},
    {"name": "single login", "call": "sql(QUERY, logins=LOGINS_SMALL.iloc[[5]])", "visible": True},
    {"name": "across a month and year end", "call": "sql(QUERY, logins=pd.DataFrame({'user_id': ['x'] * 4, 'day': ['2023-12-30', '2023-12-31', '2024-01-01', '2024-01-03']}))"},
    {"name": "leap day", "call": "sql(QUERY, logins=pd.DataFrame({'user_id': ['x'] * 3, 'day': ['2024-02-28', '2024-02-29', '2024-03-01']}))"},
    {"name": "unsorted rows", "call": "sql(QUERY, logins=LOGINS_SMALL.iloc[::-1])"},
    {"name": "random larger case", "call": "sql(QUERY, logins=BIG)"},
]
