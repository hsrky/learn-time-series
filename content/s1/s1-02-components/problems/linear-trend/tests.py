import numpy as np

rng = np.random.default_rng(10)
t = np.arange(500)
BIG = 20 + 0.3 * t + rng.normal(0, 3, 500)
BIGN = BIG.copy()
BIGN[rng.random(500) < 0.2] = np.nan

CASES = [
    {"name": "example", "call": "linear_trend([100, 110, 125, 135, 150])", "expected": "(12.5, 99.0)", "visible": True},
    {"name": "with nan", "call": "linear_trend([1, np.nan, 5])", "expected": "(2.0, 1.0)", "visible": True},
    {"name": "flat", "call": "linear_trend([4.0, 4.0, 4.0])", "expected": "(0.0, 4.0)"},
    {"name": "falling", "call": "linear_trend([10, 8, 6, 4])", "expected": "(-2.0, 10.0)"},
    {"name": "two points", "call": "linear_trend([3, 9])", "expected": "(6.0, 3.0)"},
    {"name": "matches polyfit", "call": "linear_trend(BIG)", "expected": "tuple(np.polyfit(np.arange(500), BIG, 1))"},
    {"name": "random with 20% nan", "call": "linear_trend(BIGN)"},
]
