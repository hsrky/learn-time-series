import numpy as np
import pandas as pd

idx = pd.date_range("2024-01-01", periods=4, freq="D")
S1 = pd.DataFrame({"v": [10.0, 12.0, 14.0, 20.0]}, index=idx)
S2 = pd.DataFrame({"a": [1.0, 2.0, 3.0, 4.0], "b": [5.0, 5.0, 5.0, 9.0]}, index=idx)
S3 = pd.DataFrame({"a": [1.0, np.nan, 3.0, 100.0]}, index=idx)
rng = np.random.default_rng(7)
BIG = pd.DataFrame(rng.normal(5, 3, size=(300, 3)) + np.arange(300)[:, None] * 0.1,
                   index=pd.date_range("2023-01-01", periods=300, freq="D"), columns=list("xyz"))
BIG.iloc[::17, 1] = np.nan

CASES = [
    {"name": "single column", "call": "scale_with_train_stats(S1, 3)", "visible": True,
     "expected": "pd.DataFrame({'v': [-1.224744871391589, 0.0, 1.224744871391589, 4.898979485566356]}, index=S1.index)"},
    {"name": "constant column becomes zero", "call": "scale_with_train_stats(S2, 3)", "visible": True,
     "expected": "pd.DataFrame({'a': [-1.224744871391589, 0.0, 1.224744871391589, 2.449489742783178], 'b': [0.0, 0.0, 0.0, 0.0]}, index=S2.index)"},
    {"name": "NaN is ignored", "call": "scale_with_train_stats(S3, 3)", "visible": True,
     "expected": "pd.DataFrame({'a': [-1.0, np.nan, 1.0, 98.0]}, index=S3.index)"},
    {"name": "all rows are train", "call": "scale_with_train_stats(S1, 4).mean().round(9).tolist()",
     "expected": "[0.0]"},
    {"name": "single train row", "call": "scale_with_train_stats(S1, 1)",
     "expected": "pd.DataFrame({'v': [0.0, 0.0, 0.0, 0.0]}, index=S1.index)"},
    {"name": "test must not change the scaler", "call": "scale_with_train_stats(S1.assign(v=[10.0, 12.0, 14.0, 1e9]), 3).iloc[:3]",
     "expected": "pd.DataFrame({'v': [-1.224744871391589, 0.0, 1.224744871391589]}, index=S1.index[:3])"},
    {"name": "larger random table", "call": "scale_with_train_stats(BIG, 200)"},
]
