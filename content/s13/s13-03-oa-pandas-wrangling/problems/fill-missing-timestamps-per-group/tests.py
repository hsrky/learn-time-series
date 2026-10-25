import numpy as np
import pandas as pd

D1 = pd.DataFrame({"store": ["A", "A", "B"],
                   "date": pd.to_datetime(["2024-01-01", "2024-01-04", "2024-01-02"]),
                   "sales": [5, 7, 3]})
D2 = pd.DataFrame({"store": ["B", "A", "A", "B"],
                   "date": pd.to_datetime(["2024-03-03", "2024-03-05", "2024-03-01", "2024-03-01"]),
                   "sales": [4, 9, 2, 8]})
D3 = pd.DataFrame({"store": ["Z"], "date": pd.to_datetime(["2024-05-05"]), "sales": [11]})
D4 = pd.DataFrame({"store": [], "date": pd.to_datetime([]), "sales": []})
rng = np.random.default_rng(7)
rows = []
for st in ["s1", "s2", "s3", "s4"]:
    days = pd.date_range("2024-01-01", periods=120, freq="D")
    keep = rng.random(120) > 0.3
    for d, k in zip(days, keep):
        if k:
            rows.append((st, d, int(rng.integers(1, 50))))
D5 = pd.DataFrame(rows, columns=["store", "date", "sales"]).sample(frac=1.0, random_state=1).reset_index(drop=True)

CASES = [
    {"name": "two stores", "call": "fill_missing_days(D1)", "visible": True,
     "expected": "pd.DataFrame({'store': list('AAAAB'), 'date': pd.to_datetime(['2024-01-01','2024-01-02','2024-01-03','2024-01-04','2024-01-02']), 'sales': [5,0,0,7,3]})"},
    {"name": "unsorted input", "call": "fill_missing_days(D2)", "visible": True,
     "expected": "pd.DataFrame({'store': list('AAAAABBB'), 'date': pd.to_datetime(['2024-03-01','2024-03-02','2024-03-03','2024-03-04','2024-03-05','2024-03-01','2024-03-02','2024-03-03']), 'sales': [2,0,0,0,9,8,0,4]})"},
    {"name": "single row", "call": "fill_missing_days(D3)"},
    {"name": "empty", "call": "fill_missing_days(D4)", "check_index": False},
    {"name": "larger random", "call": "fill_missing_days(D5)"},
]
