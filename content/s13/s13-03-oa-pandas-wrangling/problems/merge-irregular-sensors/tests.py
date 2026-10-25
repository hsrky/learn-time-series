import numpy as np
import pandas as pd

def T(s):
    return pd.Timestamp("2024-06-01 " + s)

A1 = pd.DataFrame({"device": ["m1", "m1", "m2"], "time": [T("10:00:30"), T("10:03:00"), T("10:00:30")], "temp": [20.0, 21.0, 19.0]})
B1 = pd.DataFrame({"device": ["m1", "m1", "m2"], "time": [T("10:00:00"), T("10:00:50"), T("10:05:00")], "humidity": [40.0, 45.0, 50.0]})

# exact match and exact tolerance, unsorted input
A2 = pd.DataFrame({"device": ["m1", "m1", "m1"], "time": [T("10:02:00"), T("10:00:00"), T("10:01:00")], "temp": [3.0, 1.0, 2.0]})
B2 = pd.DataFrame({"device": ["m1", "m1"], "time": [T("10:01:00"), T("09:59:00")], "humidity": [70.0, 60.0]})

A3 = pd.DataFrame({"device": ["m1"], "time": [T("10:00:00")], "temp": [1.0]})
B3 = pd.DataFrame({"device": pd.Series([], dtype=object), "time": pd.to_datetime([]), "humidity": pd.Series([], dtype=float)})

rng = np.random.default_rng(11)
devs = ["d%d" % i for i in range(5)]
ta = pd.Timestamp("2024-06-01") + pd.to_timedelta(rng.integers(0, 20000, 400), unit="s")
A4 = pd.DataFrame({"device": rng.choice(devs, 400), "time": ta, "temp": rng.normal(20, 3, 400).round(2)}).drop_duplicates(["device", "time"])
tb = pd.Timestamp("2024-06-01") + pd.to_timedelta(rng.integers(0, 20000, 700), unit="s")
B4 = pd.DataFrame({"device": rng.choice(devs, 700), "time": tb, "humidity": rng.uniform(30, 80, 700).round(2)})

CASES = [
    {"name": "example", "call": "attach_latest(A1, B1, 60)", "visible": True,
     "expected": "pd.DataFrame({'device': ['m1','m1','m2'], 'time': [T('10:00:30'), T('10:03:00'), T('10:00:30')], 'temp': [20.0,21.0,19.0], 'humidity': [40.0, np.nan, np.nan]})"},
    {"name": "exact match and exact tolerance", "call": "attach_latest(A2, B2, 60)", "visible": True,
     "expected": "pd.DataFrame({'device': ['m1','m1','m1'], 'time': [T('10:00:00'), T('10:01:00'), T('10:02:00')], 'temp': [1.0,2.0,3.0], 'humidity': [60.0, 70.0, 70.0]})"},
    {"name": "tolerance zero", "call": "attach_latest(A2, B2, 0)",
     "expected": "pd.DataFrame({'device': ['m1','m1','m1'], 'time': [T('10:00:00'), T('10:01:00'), T('10:02:00')], 'temp': [1.0,2.0,3.0], 'humidity': [np.nan, 70.0, np.nan]})"},
    {"name": "empty b", "call": "attach_latest(A3, B3, 100)"},
    {"name": "larger random", "call": "attach_latest(A4, B4, 300)"},
    {"name": "larger random, tight tolerance", "call": "attach_latest(A4, B4, 20)"},
]
