import numpy as np
import pandas as pd

D = pd.date_range("2024-01-01", periods=3, freq="D")
A = pd.DataFrame({"series_id": "a", "date": D, "y": [0.0, 9.0, 99.0]})
AB = pd.concat([A, pd.DataFrame({"series_id": "b", "date": D, "y": [5.0, 5.0, 5.0]})], ignore_index=True)
rng = np.random.default_rng(12)
rows = []
for k, sid in enumerate(["x", "y", "z"]):
    d = pd.date_range("2024-01-01", periods=100, freq="D")
    rows.append(pd.DataFrame({"series_id": sid, "date": d, "y": rng.gamma(3.0, 10.0 ** (k + 1), 100)}))
BIG = pd.concat(rows, ignore_index=True)

CASES = [
    {"name": "fit on rows before cutoff only", "call": "s = PerSeriesScaler()\ns.fit(A, '2024-01-03')\ns.transform(A).round(4).tolist()", "visible": True,
     "expected": "[-1.0, 1.0, 3.0]"},
    {"name": "constant series uses sd = 1", "call": "s = PerSeriesScaler(log=False)\ns.fit(AB, '2024-01-03')\ns.transform(AB[AB.series_id == 'b']).tolist()", "visible": True,
     "expected": "[0.0, 0.0, 0.0]"},
    {"name": "round trip", "call": "s = PerSeriesScaler()\ns.fit(BIG, '2024-03-01')\nnp.allclose(s.inverse_transform(BIG['series_id'], s.transform(BIG)), BIG['y'])", "visible": True,
     "expected": "True"},
    {"name": "unknown series is identity", "call": "s = PerSeriesScaler(log=False)\ns.fit(A, '2024-01-03')\ns.inverse_transform(['zzz', 'a'], [2.0, 0.0]).tolist()",
     "expected": "[2.0, 4.5]"},
    {"name": "no log, mean and sd", "call": "s = PerSeriesScaler(log=False)\ns.fit(A, '2024-01-03')\ns.transform(A).tolist()",
     "expected": "[-1.0, 1.0, 21.0]"},
    {"name": "negative forecasts are clipped to 0", "call": "s = PerSeriesScaler()\ns.fit(A, '2024-01-03')\ns.inverse_transform(['a'], [-5.0]).tolist()",
     "expected": "[0.0]"},
    {"name": "test period does not change the scaler", "call": "s = PerSeriesScaler()\ns.fit(BIG.assign(y=np.where(BIG.date >= '2024-03-01', 1e6, BIG.y)), '2024-03-01')\ns.transform(BIG[BIG.date < '2024-03-01']).round(6).tolist()[:5]"},
    {"name": "large panel transform", "call": "s = PerSeriesScaler()\ns.fit(BIG, '2024-03-01')\ns.transform(BIG)"},
]
