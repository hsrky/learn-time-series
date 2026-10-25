import numpy as np
import pandas as pd

DF = pd.DataFrame({"store": list("ABABAB"), "y": [10.0, 50.0, 20.0, 60.0, 30.0, 70.0]})
DF2 = pd.DataFrame({"store": ["x", "x", "y", "x", "z", "y"], "y": [4.0, 6.0, 100.0, 8.0, 1.0, 50.0]},
                   index=pd.date_range("2024-01-01", periods=6, freq="D"))
rng = np.random.default_rng(6)
BIG = pd.DataFrame({"store": rng.choice(list("abcdefgh"), 2000), "y": rng.gamma(2.0, 10.0, 2000)})

CASES = [
    {"name": "m = 0", "call": "expanding_target_encoding(DF, 'store', 'y')", "visible": True,
     "expected": "pd.Series([np.nan, 10.0, 10.0, 50.0, 15.0, 55.0])"},
    {"name": "m = 2", "call": "expanding_target_encoding(DF, 'store', 'y', m=2)", "visible": True,
     "expected": "pd.Series([np.nan, 10.0, 70 / 3, (50 + 160 / 3) / 3, 25.0, 44.5])"},
    {"name": "keeps the original index", "call": "expanding_target_encoding(DF2, 'store', 'y')", "visible": True},
    {"name": "single row", "call": "expanding_target_encoding(DF.iloc[:1], 'store', 'y')", "expected": "pd.Series([np.nan])"},
    {"name": "empty table", "call": "len(expanding_target_encoding(DF.iloc[:0], 'store', 'y'))", "expected": "0"},
    {"name": "changing a later target does not change earlier values", "call": "expanding_target_encoding(DF.assign(y=[10.0, 50.0, 20.0, 60.0, 30.0, 9999.0]), 'store', 'y').iloc[:5]",
     "expected": "pd.Series([np.nan, 10.0, 10.0, 50.0, 15.0])"},
    {"name": "large random table, m = 5", "call": "expanding_target_encoding(BIG, 'store', 'y', m=5)", "tol": 1e-6},
    {"name": "large random table, m = 0", "call": "expanding_target_encoding(BIG, 'store', 'y')"},
]
