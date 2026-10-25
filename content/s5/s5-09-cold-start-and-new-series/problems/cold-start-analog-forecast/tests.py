import numpy as np

rng = np.random.default_rng(2)
AGES = np.arange(40)
SHAPE = 1 - 0.7 * np.exp(-AGES / 3.0)
BIGAN = [lv * SHAPE * (1 + rng.normal(0, 0.05, 40)) for lv in rng.uniform(20, 200, 60)]
BIGNEW = list(45 * SHAPE[:8] * (1 + rng.normal(0, 0.05, 8)))
AN = [[10, 14, 18, 21, 21], [100, 100, 100, 100, 100]]

CASES = [
    {"name": "best analog", "call": "cold_start_forecast([5, 7, 9], AN, 2, k=1)", "visible": True,
     "expected": "np.array([10.5, 10.5])"},
    {"name": "average of two analogs", "call": "cold_start_forecast([5, 7, 9], AN, 2, k=2)", "visible": True},
    {"name": "no history uses raw average", "call": "cold_start_forecast([], [[1, 2, 3], [3, 4, 5], [9]], 2)", "visible": True,
     "expected": "np.array([2.0, 3.0])"},
    {"name": "no valid analog falls back to the mean", "call": "cold_start_forecast([4, 6], [[1, 2, 3]], 3)",
     "expected": "np.array([5.0, 5.0, 5.0])"},
    {"name": "zero history level", "call": "cold_start_forecast([0, 0], AN, 2)", "expected": "np.array([0.0, 0.0])"},
    {"name": "k larger than valid analogs", "call": "cold_start_forecast([5, 7, 9], AN, 2, k=10)"},
    {"name": "ties keep the lower position", "call": "cold_start_forecast([2, 2], [[1, 1, 5, 5], [3, 3, 9, 9]], 2, k=1)",
     "expected": "np.array([10.0, 10.0])"},
    {"name": "60 analogs, 8 days of history", "call": "cold_start_forecast(BIGNEW, BIGAN, 14, k=5)"},
    {"name": "60 analogs, k = 1", "call": "cold_start_forecast(BIGNEW[:4], BIGAN, 7, k=1)"},
]
