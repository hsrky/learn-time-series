import numpy as np
rng = np.random.default_rng(14)
BIG = [int(v) for v in np.cumsum(rng.integers(-3, 4, 100000))]
CASES = [
    {"name": "small", "call": "longest_stable([8, 2, 4, 7], 4)", "visible": True},
    {"name": "range 5", "call": "longest_stable([10, 1, 2, 4, 7, 2], 5)", "visible": True},
    {"name": "empty", "call": "longest_stable([], 3)"},
    {"name": "limit zero", "call": "longest_stable([4, 4, 4, 5, 5, 4], 0)"},
    {"name": "everything stable", "call": "longest_stable([1, 2, 3, 2, 1], 10)"},
    {"name": "single reading", "call": "longest_stable([7], 0)"},
    {"name": "random walk, large", "call": "longest_stable(BIG, 25)"},
]
