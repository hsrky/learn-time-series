import numpy as np
rng = np.random.default_rng(12)
BIG = [int(v) for v in rng.integers(-1000, 1000, 200000)]
DEC = list(range(50000, 0, -1))
CASES = [
    {"name": "classic", "call": "sliding_window_max([1, 3, -1, -3, 5, 3, 6, 7], 3)", "visible": True},
    {"name": "k = 1", "call": "sliding_window_max([9, 8, 7], 1)", "visible": True},
    {"name": "k equals length", "call": "sliding_window_max([2, 9, 4], 3)"},
    {"name": "k larger than length", "call": "sliding_window_max([2, 9], 5)"},
    {"name": "empty", "call": "sliding_window_max([], 2)"},
    {"name": "equal values", "call": "sliding_window_max([5, 5, 5, 5], 2)"},
    {"name": "decreasing (deque stays long)", "call": "sliding_window_max(DEC, 20000)[:3]"},
    {"name": "random large case (needs O(n))", "call": "sliding_window_max(BIG, 5000)[::997]"},
]
