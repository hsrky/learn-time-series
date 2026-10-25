import numpy as np
import pandas as pd
LOGS = pd.DataFrame({
    "user": ["ann", "ann", "ann", "bob", "ann", "ann", "ann"],
    "day": pd.to_datetime(["2024-05-01", "2024-05-02", "2024-05-03", "2024-05-02", "2024-05-05", "2024-05-06", "2024-05-02"]),
})
rng = np.random.default_rng(25)
BIG = pd.DataFrame({
    "user": ["u%d" % i for i in rng.integers(0, 20, 4000)],
    "day": pd.Timestamp("2024-01-01") + pd.to_timedelta(rng.integers(0, 120, 4000), unit="D"),
})
CASES = [
    {"name": "small log", "call": "login_islands(LOGS)", "visible": True},
    {"name": "empty", "call": "login_islands(LOGS.iloc[:0])", "visible": True},
    {"name": "one user, one day", "call": "login_islands(LOGS.iloc[[3]])"},
    {"name": "all duplicates", "call": "login_islands(pd.concat([LOGS.iloc[[0]]] * 3))"},
    {"name": "unsorted input", "call": "login_islands(LOGS.iloc[::-1])"},
    {"name": "random larger case", "call": "login_islands(BIG).head(30)"},
    {"name": "random larger case (count)", "call": "len(login_islands(BIG))"},
]
