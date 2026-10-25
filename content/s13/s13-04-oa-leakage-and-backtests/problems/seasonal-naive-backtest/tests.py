import numpy as np

rng = np.random.default_rng(9)
t = np.arange(400)
BIG = list(np.round(50 + 10 * np.sin(2 * np.pi * t / 7) + rng.normal(0, 2, 400), 3))

CASES = [
    {"name": "one fold", "call": "seasonal_naive_backtest([1, 2, 3, 1, 2, 3, 1, 2, 4], 3, 3, 1)", "expected": "1/3", "visible": True},
    {"name": "two folds", "call": "seasonal_naive_backtest([1, 2, 3, 1, 2, 3, 1, 2, 4], 3, 3, 2)", "expected": "1/6", "visible": True},
    {"name": "h larger than m wraps", "call": "seasonal_naive_backtest([5, 7, 5, 7, 5, 7, 9, 9, 9], 2, 5, 1)", "expected": "(0 + 0 + 4 + 2 + 4) / 5"},
    {"name": "season of 1 is plain naive", "call": "seasonal_naive_backtest([1, 3, 6, 10], 1, 1, 3)", "expected": "(2 + 3 + 4) / 3"},
    {"name": "perfect seasonal data", "call": "seasonal_naive_backtest([4, 5, 6] * 5, 3, 3, 2)", "expected": "0.0"},
    {"name": "minimal training window", "call": "seasonal_naive_backtest([2, 9, 4, 4, 4], 2, 3, 1)"},
    {"name": "larger random", "call": "seasonal_naive_backtest(BIG, 7, 14, 10)"},
]
