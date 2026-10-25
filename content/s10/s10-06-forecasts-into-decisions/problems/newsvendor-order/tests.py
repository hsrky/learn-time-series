import numpy as np

rng = np.random.default_rng(8)
BIG = np.maximum(rng.normal(100, 20, 5000), 0).round()
SMALL = [10, 20, 30, 40]

CASES = [
    {"name": "example: ratio 0.75", "call": "newsvendor_order(SMALL, 3, 1)", "visible": True, "expected": "30.0"},
    {"name": "all equal", "call": "newsvendor_order([5, 5, 5], 1, 1)", "visible": True, "expected": "5.0"},
    {"name": "expected cost of q=30", "call": "expected_cost(30, SMALL, 3, 1)", "visible": True, "expected": "15.0"},
    {"name": "unsorted input, ratio 0.5", "call": "newsvendor_order([40, 10, 30, 20], 1, 1)", "expected": "20.0"},
    {"name": "low ratio picks a low quantile", "call": "newsvendor_order(SMALL, 1, 9)", "expected": "10.0"},
    {"name": "float edge: ratio 0.7 with 10 samples", "call": "newsvendor_order(list(range(1, 11)), 7, 3)", "expected": "7.0"},
    {"name": "single sample", "call": "newsvendor_order([12], 2, 5)", "expected": "12.0"},
    {"name": "expected cost zero when q equals constant demand", "call": "expected_cost(5, [5, 5], 3, 2)", "expected": "0.0"},
    {"name": "large: order minimises cost among samples",
     "call": "min(sorted(set(BIG.tolist())), key=lambda c: expected_cost(c, BIG, 3, 2)) == newsvendor_order(BIG, 3, 2) or abs(expected_cost(newsvendor_order(BIG, 3, 2), BIG, 3, 2) - min(expected_cost(c, BIG, 3, 2) for c in set(BIG.tolist()))) < 1e-9",
     "expected": "True"},
    {"name": "large value", "call": "newsvendor_order(BIG, 3, 2)"},
]
