import numpy as np
import pandas as pd
EVENTS_SMALL = pd.DataFrame({
    "event_id": [1, 2, 3, 4, 5],
    "user_id": ["u1", "u2", "u1", "u1", "u1"],
    "event_time": ["2024-05-01 09:30:00", "2024-05-01 08:00:00", "2024-05-01 09:00:00", "2024-05-02 10:00:00", "2024-05-01 09:00:00"],
    "event_type": ["click", "login", "login", "buy", "view"],
})
rng = np.random.default_rng(35)
n = 4000
BIG = pd.DataFrame({
    "event_id": np.arange(n),
    "user_id": ["u%d" % i for i in rng.integers(0, 100, n)],
    "event_time": (pd.Timestamp("2024-01-01") + pd.to_timedelta(rng.integers(0, 20000, n) * 60, unit="s")).strftime("%Y-%m-%d %H:%M:%S"),
    "event_type": rng.choice(["view", "click", "buy"], n),
}).sample(frac=1, random_state=4)
CASES = [
    {"name": "small with a tie", "call": "sql(QUERY, events=EVENTS_SMALL)", "visible": True},
    {"name": "single event", "call": "sql(QUERY, events=EVENTS_SMALL.iloc[:1])", "visible": True},
    {"name": "tie only on time", "call": "sql(QUERY, events=EVENTS_SMALL.iloc[[2, 4]])"},
    {"name": "reversed order", "call": "sql(QUERY, events=EVENTS_SMALL.iloc[::-1])"},
    {"name": "random larger case (shuffled, with ties)", "call": "sql(QUERY, events=BIG)"},
]
