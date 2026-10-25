import numpy as np
import pandas as pd

COLS = ["date", "series_id", "yhat", "version"]
def mk(rows):
    df = pd.DataFrame(rows, columns=COLS)
    df["date"] = pd.to_datetime(df["date"])
    return df

E1 = mk([("2024-01-01", "A", 10.0, "v1"), ("2024-01-01", "B", 20.0, "v1")])
N1 = mk([("2024-01-01", "B", 25.0, "v2"), ("2024-01-02", "A", 30.0, "v2")])
EMPTY = mk([])
N_DUP = mk([("2024-01-01", "A", 1.0, "v2"), ("2024-01-01", "A", 2.0, "v3")])

rng = np.random.default_rng(11)
def rnd(n, ver):
    return pd.DataFrame({"date": pd.Timestamp("2024-01-01") + pd.to_timedelta(rng.integers(0, 30, n), unit="D"),
                         "series_id": rng.choice([f"s{i}" for i in range(20)], n),
                         "yhat": rng.normal(100, 10, n), "version": ver})
ER, NR = rnd(500, "v1"), rnd(300, "v2")

def _up(e, n):
    b = pd.concat([d for d in (e, n) if len(d)], ignore_index=True).drop_duplicates(["date", "series_id"], keep="last")
    return b.sort_values(["date", "series_id"]).reset_index(drop=True)

CASES = [
    {"name": "replace one, add one", "call": "upsert_forecasts(E1, N1)", "visible": True,
     "expected": "mk([('2024-01-01','A',10.0,'v1'),('2024-01-01','B',25.0,'v2'),('2024-01-02','A',30.0,'v2')])"},
    {"name": "idempotent", "call": "upsert_forecasts(upsert_forecasts(E1, N1), N1)", "visible": True,
     "expected": "_up(E1, N1)"},
    {"name": "last duplicate in new wins", "call": "upsert_forecasts(E1, N_DUP)", "visible": True},
    {"name": "empty existing", "call": "upsert_forecasts(EMPTY, N1)"},
    {"name": "empty new", "call": "upsert_forecasts(E1, EMPTY)"},
    {"name": "inputs unchanged", "call": "(lambda e, n: (upsert_forecasts(e, n), len(e), len(n))[1:])(E1.copy(), N1.copy())", "expected": "(2, 2)"},
    {"name": "random large case", "call": "upsert_forecasts(ER, NR)"},
    {"name": "random idempotent", "call": "upsert_forecasts(upsert_forecasts(ER, NR), NR)", "expected": "_up(ER, NR)"},
]
