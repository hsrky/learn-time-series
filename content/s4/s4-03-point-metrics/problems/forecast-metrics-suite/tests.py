import numpy as np

nan = float("nan")
rng = np.random.default_rng(11)
BY = rng.gamma(2.0, 20.0, 1000)
BF = BY * rng.normal(1.0, 0.15, 1000)

CASES = [
    {"name": "basic example", "call": "point_metrics([10, 20, 30, 40], [12, 18, 33, 36])", "visible": True,
     "expected": "{'mae': 2.75, 'rmse': 2.8722813232690143, 'mape': 12.5, 'smape': 12.19, 'wape': 0.11}", "tol": 0.01},
    {"name": "zero actual is skipped in MAPE", "call": "point_metrics([0, 10], [3, 12])", "visible": True,
     "expected": "{'mae': 2.5, 'rmse': 2.5495097567963922, 'mape': 20.0, 'smape': 100*(2*3/3 + 2*2/22)/2, 'wape': 0.5}"},
    {"name": "perfect forecast", "call": "point_metrics([1, 2, 3], [1, 2, 3])", "visible": True,
     "expected": "{'mae': 0.0, 'rmse': 0.0, 'mape': 0.0, 'smape': 0.0, 'wape': 0.0}"},
    {"name": "all zero actuals", "call": "point_metrics([0, 0], [0, 1])",
     "expected": "{'mae': 0.5, 'rmse': 0.7071067811865476, 'mape': nan, 'smape': 100.0, 'wape': nan}"},
    {"name": "both zero counts as perfect for sMAPE", "call": "point_metrics([0, 5], [0, 5])",
     "expected": "{'mae': 0.0, 'rmse': 0.0, 'mape': 0.0, 'smape': 0.0, 'wape': 0.0}"},
    {"name": "empty input", "call": "point_metrics([], [])",
     "expected": "{'mae': nan, 'rmse': nan, 'mape': nan, 'smape': nan, 'wape': nan}"},
    {"name": "negative values", "call": "point_metrics(np.array([-10.0, 10.0]), np.array([-5.0, 15.0]))"},
    {"name": "large random", "call": "point_metrics(BY, BF)"},
]
