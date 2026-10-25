import numpy as np

nan = float("nan")
rng = np.random.default_rng(21)
BY = rng.normal(50, 8, 1000)
BL = np.full(1000, 50 - 1.2816 * 6)
BU = np.full(1000, 50 + 1.2816 * 6)

CASES = [
    {"name": "three points", "call": "interval_metrics([100, 120, 85], [90, 90, 90], [110, 110, 110], 0.2)", "visible": True,
     "expected": "{'coverage': 1/3, 'mean_width': 20.0, 'interval_score': 70.0, 'calibration_gap': 1/3 - 0.8}"},
    {"name": "all inside", "call": "interval_metrics([5, 5], [4, 0], [6, 10], 0.1)", "visible": True,
     "expected": "{'coverage': 1.0, 'mean_width': 6.0, 'interval_score': 6.0, 'calibration_gap': 0.1}"},
    {"name": "borders count as inside", "call": "interval_metrics([4, 6], [4, 4], [6, 6], 0.5)", "visible": True,
     "expected": "{'coverage': 1.0, 'mean_width': 2.0, 'interval_score': 2.0, 'calibration_gap': 0.5}"},
    {"name": "reversed interval is swapped", "call": "interval_metrics([5], [10], [0], 0.2)",
     "expected": "{'coverage': 1.0, 'mean_width': 10.0, 'interval_score': 10.0, 'calibration_gap': 0.2}"},
    {"name": "empty", "call": "interval_metrics([], [], [], 0.2)",
     "expected": "{'coverage': nan, 'mean_width': nan, 'interval_score': nan, 'calibration_gap': nan}"},
    {"name": "narrow alpha penalizes more", "call": "interval_metrics([20], [0], [10], 0.05)",
     "expected": "{'coverage': 0.0, 'mean_width': 10.0, 'interval_score': 10 + 40 * 10, 'calibration_gap': -0.95}"},
    {"name": "random overconfident intervals", "call": "interval_metrics(BY, BL, BU, 0.2)"},
]
