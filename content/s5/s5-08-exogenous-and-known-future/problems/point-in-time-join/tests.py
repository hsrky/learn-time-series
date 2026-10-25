import numpy as np
import pandas as pd

EV = pd.DataFrame({"id": ["a", "a", "b"],
                   "time": pd.to_datetime(["2024-01-03 08:00", "2024-01-01 09:00", "2024-01-02 10:00"]),
                   "units": [9, 5, 3]}, index=[10, 11, 12])
FE = pd.DataFrame({"id": ["a", "a", "a", "b"],
                   "available_at": pd.to_datetime(["2024-01-03 09:00", "2023-12-31 00:00", "2024-01-01 12:00", "2024-01-02 11:00"]),
                   "value": [8.0, 10.0, 9.0, 100.0]})
rng = np.random.default_rng(15)
BE = pd.DataFrame({"id": rng.integers(0, 20, 1500),
                   "time": pd.Timestamp("2024-01-01") + pd.to_timedelta(rng.integers(0, 24 * 60 * 30, 1500), unit="min")})
BF = pd.DataFrame({"id": rng.integers(0, 20, 400),
                   "available_at": pd.Timestamp("2023-12-25") + pd.to_timedelta(rng.integers(0, 24 * 60 * 40, 400), unit="min"),
                   "value": rng.normal(size=400)})

CASES = [
    {"name": "latest value at or before the event", "call": "pit_join(EV, FE)", "visible": True},
    {"name": "tolerance drops stale matches", "call": "pit_join(EV, FE, tolerance_hours=24)", "visible": True},
    {"name": "exact timestamp counts", "call": "pit_join(EV.iloc[:1].assign(time=pd.to_datetime(['2024-01-03 09:00'])), FE)['feature_value'].tolist()", "visible": True,
     "expected": "[8.0]"},
    {"name": "no feature for this id", "call": "pit_join(EV.assign(id='zzz'), FE)['feature_value'].isna().all()", "expected": "True"},
    {"name": "event before every feature", "call": "pit_join(EV.assign(time=pd.Timestamp('2020-01-01')), FE)['feature_value'].isna().all()", "expected": "True"},
    {"name": "empty features", "call": "pit_join(EV, FE.iloc[0:0])"},
    {"name": "original order and index are kept", "call": "pit_join(EV, FE).index.tolist()", "expected": "[10, 11, 12]"},
    {"name": "large random join", "call": "pit_join(BE, BF)"},
    {"name": "large random join with tolerance", "call": "pit_join(BE, BF, tolerance_hours=48)"},
]
