import numpy as np
import pandas as pd
LOG = pd.DataFrame({
    "user": ["ann", "bob", "ann", "ann"],
    "ts": pd.to_datetime(["2024-05-01 09:00", "2024-05-01 09:05", "2024-05-01 09:10", "2024-05-01 10:00"]),
})
rng = np.random.default_rng(23)
BIG = pd.DataFrame({
    "user": ["u%d" % i for i in rng.integers(0, 30, 5000)],
    "ts": pd.Timestamp("2024-01-01") + pd.to_timedelta(rng.integers(0, 3_000_000, 5000), unit="s"),
})
CASES = [
    {"name": "small log", "call": "sessionize_df(LOG)", "visible": True},
    {"name": "empty", "call": "sessionize_df(LOG.iloc[:0])", "visible": True},
    {"name": "gap exactly 30 minutes", "call": "sessionize_df(pd.DataFrame({'user': ['a', 'a'], 'ts': pd.to_datetime(['2024-01-01 00:00', '2024-01-01 00:30'])}))"},
    {"name": "gap just over 30 minutes", "call": "sessionize_df(pd.DataFrame({'user': ['a', 'a'], 'ts': pd.to_datetime(['2024-01-01 00:00:00', '2024-01-01 00:30:01'], format='ISO8601')}))"},
    {"name": "input is not changed", "call": "x = LOG.copy()\n_ = sessionize_df(x)\nx", "expected": "LOG"},
    {"name": "random larger case", "call": "sessionize_df(BIG).head(30)"},
    {"name": "random larger case (count)", "call": "len(sessionize_df(BIG))"},
]
