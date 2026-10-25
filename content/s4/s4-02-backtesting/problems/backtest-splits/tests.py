import numpy as np

CASES = [
    {"name": "expanding, default step", "call": "list(backtest_splits(10, 6, 2))", "visible": True},
    {"name": "sliding window with gap", "call": "list(backtest_splits(12, 4, 2, step=2, window=3, gap=1))", "visible": True,
     "expected": "[(np.array([1,2,3]), np.array([5,6])), (np.array([3,4,5]), np.array([7,8])), (np.array([5,6,7]), np.array([9,10]))]"},
    {"name": "step 1 overlapping tests", "call": "list(backtest_splits(8, 5, 3, step=1))", "visible": True},
    {"name": "no complete fold", "call": "list(backtest_splits(5, 5, 1))", "expected": "[]"},
    {"name": "last fold fits exactly", "call": "[int(t[-1]) for _, t in backtest_splits(100, 60, 10)]",
     "expected": "[69, 79, 89, 99]"},
    {"name": "window larger than history", "call": "list(backtest_splits(9, 3, 2, window=50))"},
    {"name": "gap drops last fold", "call": "len(list(backtest_splits(100, 60, 10, gap=5)))", "expected": "3"},
    {"name": "large run", "call": "[(int(a[0]), int(a[-1]), int(b[0]), int(b[-1])) for a, b in backtest_splits(5000, 1000, 24, step=7, window=700, gap=3)]"},
]
