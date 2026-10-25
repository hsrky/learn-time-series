import numpy as np
import pandas as pd

rng = np.random.default_rng(8)
YT = list(rng.integers(0, 9000, 400).astype(float)); YP = list(rng.uniform(0, 9000, 400))
DF1 = pd.DataFrame({"Open": [1, 0, np.nan], "pred": [50.0, 40.0, 30.0]})
DF2 = pd.DataFrame({"Open": [0, 0, 1, 1], "pred": [5.0, 6.0, 7.0, 8.0]}, index=[10, 20, 30, 40])
DF3 = pd.DataFrame({"Open": [], "pred": []})

CASES = [
    {"name": "zero actual is ignored", "call": "rmspe([100, 0, 200], [110, 5, 180])", "expected": "0.1", "visible": True},
    {"name": "open rule with NaN", "call": "apply_open_rule(DF1)", "expected": "pd.Series([50.0, 0.0, 30.0])", "visible": True},
    {"name": "all zero actuals", "call": "rmspe([0, 0], [3, 4])", "expected": "0.0"},
    {"name": "perfect forecast", "call": "rmspe([5, 10], [5, 10])", "expected": "0.0"},
    {"name": "percentage is relative to the actual", "call": "rmspe([10, 1000], [20, 1000])", "expected": "math.sqrt(0.5)"},
    {"name": "open rule keeps the index", "call": "apply_open_rule(DF2)", "expected": "pd.Series([0.0, 0.0, 7.0, 8.0], index=[10, 20, 30, 40])"},
    {"name": "empty frame", "call": "apply_open_rule(DF3)", "check_index": False},
    {"name": "larger random", "call": "rmspe(YT, YP)"},
]
