import numpy as np
rng = np.random.default_rng(7)
BIG = list(np.round(rng.normal(50, 2, 400), 2))
for p in (100, 250, 251, 399):
    BIG[p] += 25
CASES = [
    {"name": "flat history", "call": "rolling_zscore_anomalies([1, 1, 1, 1, 1, 9, 1, 1], 5, 3)", "visible": True},
    {"name": "one spike", "call": "rolling_zscore_anomalies([10, 11, 9, 10, 12, 10, 30, 11], 4, 3)", "visible": True},
    {"name": "no anomaly", "call": "rolling_zscore_anomalies([1, 2, 3, 4, 5, 6], 3, 3)"},
    {"name": "series shorter than window", "call": "rolling_zscore_anomalies([5, 6], 3, 3)"},
    {"name": "window 1 (std always 0)", "call": "rolling_zscore_anomalies([1, 1, 2, 2, 2, 5], 1, 3)"},
    {"name": "negative spike", "call": "rolling_zscore_anomalies([20, 21, 19, 20, 22, -30, 21], 4, 3)"},
    {"name": "random larger case", "call": "rolling_zscore_anomalies(BIG, 30, 4)"},
]
