import numpy as np

rng = np.random.default_rng(14)
BIG = {}
for k in range(40):
    level = rng.uniform(5, 500)
    t = np.arange(80)
    BIG[f"s{k}"] = list(level * (1 + 0.3 * np.sin(2 * np.pi * t / 7 + k) + rng.normal(0, 0.03, 80)))

CASES = [
    {"name": "two lines with different scale", "call": "global_ar_forecast({'a': [1, 2, 3, 4, 5], 'b': [10, 20, 30, 40, 50]}, 2)", "visible": True,
     "expected": "{'a': 6.0, 'b': 60.0}", "tol": 1e-6},
    {"name": "constant series", "call": "global_ar_forecast({'x': [5, 5, 5, 5], 'y': [2, 2, 2, 2]}, 2)", "visible": True,
     "expected": "{'x': 5.0, 'y': 2.0}", "tol": 1e-6},
    {"name": "short series gets nan", "call": "global_ar_forecast({'a': [1, 2, 3, 4, 5], 'b': [1.0]}, 2)", "visible": True,
     "expected": "{'a': 6.0, 'b': float('nan')}", "tol": 1e-6},
    {"name": "no training rows", "call": "global_ar_forecast({'a': [1, 2], 'b': [3, 4]}, 2)",
     "expected": "{'a': float('nan'), 'b': float('nan')}"},
    {"name": "zero window scale", "call": "global_ar_forecast({'a': [0, 0, 0, 1, 2, 3], 'b': [0, 0, 0]}, 2)"},
    {"name": "p = 1", "call": "global_ar_forecast({'a': [2, 4, 6, 8], 'b': [1, 2, 3]}, 1)"},
    {"name": "40 seasonal series, p = 7", "call": "global_ar_forecast(BIG, 7)", "tol": 1e-5},
    {"name": "40 seasonal series, p = 14", "call": "global_ar_forecast(BIG, 14)", "tol": 1e-5},
]
