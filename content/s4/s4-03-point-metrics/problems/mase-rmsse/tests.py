import numpy as np

nan = float("nan")
TR = [10, 12, 11, 13, 15, 14, 16, 18]
rng = np.random.default_rng(5)
T = np.arange(400)
BTR = 100 + 10 * np.sin(2 * np.pi * T / 7) + rng.normal(0, 2, 400)
BY = 100 + 10 * np.sin(2 * np.pi * (T[:28] + 400) / 7) + rng.normal(0, 2, 28)
BF = 100 + 10 * np.sin(2 * np.pi * (T[:28] + 400) / 7)

CASES = [
    {"name": "mase example", "call": "mase([10, 20, 30, 40], [12, 18, 33, 36], TR)", "visible": True,
     "expected": "2.75 / (12 / 7)"},
    {"name": "rmsse example", "call": "rmsse([10, 20, 30, 40], [12, 18, 33, 36], TR)", "visible": True,
     "expected": "float(np.sqrt(8.25 / (np.diff(TR) ** 2).mean()))"},
    {"name": "seasonal scale m=2", "call": "mase([4], [6], [1, 5, 2, 6, 3, 7], m=2)", "visible": True,
     "expected": "2.0"},
    {"name": "flat training series", "call": "mase([1, 2], [1, 3], [5, 5, 5, 5])", "expected": "nan"},
    {"name": "train too short", "call": "rmsse([1], [2], [3], m=1)", "expected": "nan"},
    {"name": "perfect forecast is 0", "call": "mase([1, 2, 3], [1, 2, 3], TR)", "expected": "0.0"},
    {"name": "seasonal m=7 on random data", "call": "mase(BY, BF, BTR, m=7)"},
    {"name": "rmsse m=7 on random data", "call": "rmsse(BY, BF, BTR, m=7)"},
]
