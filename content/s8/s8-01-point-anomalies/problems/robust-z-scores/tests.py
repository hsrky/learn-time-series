import numpy as np
rng = np.random.default_rng(3)
BIG = list(np.round(rng.normal(0, 1, 500), 3))
BIG[10] = 40.0; BIG[400] = -35.0
CASES = [
    {"name": "one spike", "call": "robust_anomalies([10, 12, 11, 13, 40])", "visible": True},
    {"name": "MAD is zero", "call": "robust_anomalies([5, 5, 5, 5, 9, 5])", "visible": True},
    {"name": "no anomaly", "call": "robust_anomalies([1, 2, 3, 4, 5])"},
    {"name": "single value", "call": "robust_anomalies([7])"},
    {"name": "two outliers, one low", "call": "robust_anomalies([100, 101, 99, 100, 102, 98, 10, 300])"},
    {"name": "custom threshold", "call": "robust_anomalies([10, 12, 11, 13, 16], 1.5)"},
    {"name": "random larger case", "call": "robust_anomalies(BIG)"},
]
