import numpy as np
import pandas as pd

B1 = pd.DataFrame({"time_id": [5, 5, 5], "seconds_in_bucket": [0, 1, 2],
                   "bid_price1": [100.0, 101.0, 100.0], "ask_price1": [100.0, 101.0, 100.0],
                   "bid_size1": [10, 10, 10], "ask_size1": [10, 10, 10]})
B2 = pd.DataFrame({"time_id": [2, 1, 1, 2, 1], "seconds_in_bucket": [1, 2, 0, 0, 1],
                   "bid_price1": [10.0, 20.0, 20.0, 10.0, 20.4], "ask_price1": [10.2, 20.2, 20.2, 10.2, 20.6],
                   "bid_size1": [5, 8, 8, 5, 9], "ask_size1": [7, 6, 6, 7, 5]})
B3 = pd.DataFrame({"time_id": [9], "seconds_in_bucket": [0], "bid_price1": [1.0], "ask_price1": [1.1],
                   "bid_size1": [1], "ask_size1": [1]})
B4 = pd.DataFrame({c: [] for c in ["time_id", "seconds_in_bucket", "bid_price1", "ask_price1", "bid_size1", "ask_size1"]})
rng = np.random.default_rng(23)
rows = []
for t in range(30):
    n = int(rng.integers(5, 40))
    sec = np.sort(rng.choice(600, n, replace=False))
    mid = 100 * np.exp(np.cumsum(rng.normal(0, 0.0005, n)))
    sp = rng.uniform(0.01, 0.05, n)
    rows.append(pd.DataFrame({"time_id": t, "seconds_in_bucket": sec, "bid_price1": mid - sp / 2, "ask_price1": mid + sp / 2,
                              "bid_size1": rng.integers(1, 300, n), "ask_size1": rng.integers(1, 300, n)}))
B5 = pd.concat(rows).sample(frac=1.0, random_state=5)

CASES = [
    {"name": "wap closer to the bid", "call": "wap(100, 101, 10, 30)", "expected": "100.25", "visible": True},
    {"name": "one window of three snapshots", "call": "realized_volatility(B1)", "visible": True,
     "expected": "pd.DataFrame({'time_id': [5], 'rv': [math.sqrt(2) * math.log(1.01)]})", "tol": 1e-9},
    {"name": "wap on arrays", "call": "wap(np.array([1.0, 2.0]), np.array([1.5, 2.5]), np.array([1, 3]), np.array([1, 1]))",
     "expected": "np.array([1.25, 2.375])"},
    {"name": "two windows, unsorted, no cross-window return", "call": "realized_volatility(B2)"},
    {"name": "single snapshot gives 0", "call": "realized_volatility(B3)", "expected": "pd.DataFrame({'time_id': [9], 'rv': [0.0]})"},
    {"name": "empty", "call": "realized_volatility(B4)", "check_index": False},
    {"name": "larger random", "call": "realized_volatility(B5)"},
]
