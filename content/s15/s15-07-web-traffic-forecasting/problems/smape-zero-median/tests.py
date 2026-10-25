import numpy as np

rng = np.random.default_rng(12)
YT = rng.poisson(5, 500).astype(float); YT[rng.choice(500, 40, replace=False)] = np.nan
YP = rng.poisson(5, 500).astype(float)
H = list(rng.poisson(20, 120).astype(float)); H[100:104] = [np.nan] * 4

CASES = [
    {"name": "zero vs zero", "call": "smape([100, 0, 50], [110, 0, 50])", "expected": "200 * 10 / 210 / 3", "visible": True},
    {"name": "median ignores NaN", "call": "median_forecast([5, np.nan, 7, 9], 3, 3)", "expected": "np.array([8.0, 8.0, 8.0])", "visible": True},
    {"name": "actual zero, prediction positive is 200", "call": "smape([0], [3])", "expected": "200.0"},
    {"name": "NaN actual ignored", "call": "smape([np.nan, 10], [5, 10])", "expected": "0.0"},
    {"name": "all NaN actuals", "call": "smape([np.nan, np.nan], [1, 2])", "expected": "0.0"},
    {"name": "all-NaN window gives 0", "call": "median_forecast([1, 2, np.nan, np.nan], 2, 2)", "expected": "np.array([0.0, 0.0])"},
    {"name": "window longer than history", "call": "median_forecast([4, 6], 2, 10)", "expected": "np.array([5.0, 5.0])"},
    {"name": "larger random smape", "call": "smape(YT, YP)"},
    {"name": "larger random median", "call": "median_forecast(H, 60, 14)"},
]
