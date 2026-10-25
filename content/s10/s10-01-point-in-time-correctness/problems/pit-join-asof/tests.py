import numpy as np
import pandas as pd

L1 = pd.DataFrame({"entity": ["A"], "ts": pd.to_datetime(["2024-01-02 12:00"]), "label": [1]})
F1 = pd.DataFrame({"entity": ["A", "A"], "feature_ts": pd.to_datetime(["2024-01-03 02:00", "2024-01-02 02:00"]),
                   "x": [20.0, 10.0]})

L2 = pd.DataFrame({"entity": ["B", "A", "A", "B"],
                   "ts": pd.to_datetime(["2024-01-05 10:00", "2024-01-05 10:00", "2024-01-01 00:00", "2024-01-02 00:00"]),
                   "label": [4, 3, 2, 1]})
F2 = pd.DataFrame({"entity": ["A", "B", "A", "B"],
                   "feature_ts": pd.to_datetime(["2024-01-02 00:00", "2024-01-02 00:00", "2024-01-05 10:00", "2024-01-04 00:00"]),
                   "x": [1.0, 2.0, 3.0, 4.0], "y": [10.0, 20.0, 30.0, 40.0]})

rng = np.random.default_rng(7)
n, m = 400, 300
LB = pd.DataFrame({"entity": rng.choice(["s1", "s2", "s3"], n),
                   "ts": pd.Timestamp("2024-01-01") + pd.to_timedelta(rng.integers(0, 10 * 24 * 60, n), unit="min"),
                   "label": rng.normal(size=n)})
FB = pd.DataFrame({"entity": rng.choice(["s1", "s2", "s3", "s4"], m),
                   "feature_ts": pd.Timestamp("2024-01-01") + pd.to_timedelta(rng.integers(0, 10 * 24 * 60, m), unit="min"),
                   "f1": rng.normal(size=m), "f2": rng.integers(0, 100, m).astype(float)})

CASES = [
    {"name": "future value is not used", "call": "point_in_time_join(L1, F1)", "visible": True,
     "expected": "pd.DataFrame({'entity':['A'],'ts':pd.to_datetime(['2024-01-02 12:00']),'label':[1],'x':[10.0]})"},
    {"name": "unsorted inputs, two features, order kept", "call": "point_in_time_join(L2, F2)", "visible": True},
    {"name": "tolerance gives NaN", "call": "point_in_time_join(L2, F2, pd.Timedelta('2D'))", "visible": True},
    {"name": "exact match is allowed", "call": "point_in_time_join(L2, F2)['x'].tolist()",
     "expected": "[4.0, 3.0, float('nan'), 2.0]"},
    {"name": "entity without features", "call": "point_in_time_join(L1.assign(entity='Z'), F1)['x'].isna().tolist()", "expected": "[True]"},
    {"name": "inputs not modified", "call": "(lambda a, b: (point_in_time_join(a, b), a.columns.tolist(), b.columns.tolist())[1:])(L2.copy(), F2.copy())",
     "expected": "(['entity','ts','label'], ['entity','feature_ts','x','y'])"},
    {"name": "random large case", "call": "point_in_time_join(LB, FB)"},
    {"name": "random large case with tolerance", "call": "point_in_time_join(LB, FB, pd.Timedelta('12h'))"},
]
