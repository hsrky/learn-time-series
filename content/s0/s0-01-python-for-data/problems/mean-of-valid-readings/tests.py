import random

random.seed(7)
BIG = [None if random.random() < 0.3 else round(random.uniform(-5, 40), 2) for _ in range(5000)]

CASES = [
    {"name": "one missing", "call": "mean_valid([18.5, None, 21.5])", "expected": "20.0", "visible": True},
    {"name": "all missing", "call": "mean_valid([None, None])", "expected": "float('nan')", "visible": True},
    {"name": "no missing", "call": "mean_valid([1, 2, 3, 4])", "expected": "2.5", "visible": True},
    {"name": "empty list", "call": "mean_valid([])", "expected": "float('nan')"},
    {"name": "zero is valid", "call": "mean_valid([0, None, 0, 6])", "expected": "2.0"},
    {"name": "negative values", "call": "mean_valid([-4.0, None, 2.0])", "expected": "-1.0"},
    {"name": "random 5000", "call": "mean_valid(BIG)"},
]
