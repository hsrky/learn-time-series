import numpy as np
import pandas as pd
ORDERS_SMALL = pd.DataFrame({
    "store": ["A", "A", "A", "B", "B"],
    "day": ["2024-01-01", "2024-01-02", "2024-01-02", "2024-01-01", "2024-01-03"],
    "amount": [10.0, 5.0, 7.0, 100.0, 1.0],
})
rng = np.random.default_rng(32)
ORDERS_BIG = pd.DataFrame({
    "store": ["S%d" % i for i in rng.integers(0, 8, 3000)],
    "day": pd.Timestamp("2024-01-01") + pd.to_timedelta(rng.integers(0, 60, 3000), unit="D"),
    "amount": np.round(rng.uniform(1, 100, 3000), 2),
})
ORDERS_BIG["day"] = ORDERS_BIG["day"].dt.strftime("%Y-%m-%d")
CASES = [
    {"name": "small with a tie", "call": "sql(QUERY, orders=ORDERS_SMALL)", "visible": True},
    {"name": "single order", "call": "sql(QUERY, orders=ORDERS_SMALL.iloc[:1])", "visible": True},
    {"name": "reversed input", "call": "sql(QUERY, orders=ORDERS_SMALL.iloc[::-1])"},
    {"name": "negative amounts (refunds)", "call": "sql(QUERY, orders=pd.DataFrame({'store': ['A', 'A', 'A'], 'day': ['2024-01-01', '2024-01-02', '2024-01-03'], 'amount': [50.0, -20.0, 5.0]}))"},
    {"name": "random larger case", "call": "sql(QUERY, orders=ORDERS_BIG)", "tol": 1e-6},
]
