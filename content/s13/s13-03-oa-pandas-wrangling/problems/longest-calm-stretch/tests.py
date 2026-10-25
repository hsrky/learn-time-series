import numpy as np

rng = np.random.default_rng(5)
BIG = list(np.cumsum(rng.integers(-3, 4, 5000)))

CASES = [
    {"name": "two runs of 3", "call": "longest_calm_stretch([10, 11, 11, 20, 21, 22, 40], 1)", "expected": "3", "visible": True},
    {"name": "flat", "call": "longest_calm_stretch([5, 5, 5], 0)", "expected": "3", "visible": True},
    {"name": "empty", "call": "longest_calm_stretch([], 1)", "expected": "0"},
    {"name": "single", "call": "longest_calm_stretch([7], 0)", "expected": "1"},
    {"name": "no calm pair", "call": "longest_calm_stretch([1, 10, 1, 10], 2)", "expected": "1"},
    {"name": "exactly tol is calm", "call": "longest_calm_stretch([0, 2, 4, 6, 20], 2)", "expected": "4"},
    {"name": "drifting slowly is still calm", "call": "longest_calm_stretch([0, 1, 2, 3, 4, 5], 1)", "expected": "6"},
    {"name": "larger random", "call": "longest_calm_stretch(BIG, 2)"},
]
