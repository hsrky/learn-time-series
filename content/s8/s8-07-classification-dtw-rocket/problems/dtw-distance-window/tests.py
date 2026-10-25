import numpy as np
rng = np.random.default_rng(2)
A = list(np.round(np.sin(np.linspace(0, 6, 300)) + rng.normal(0, 0.1, 300), 3))
B = list(np.round(np.sin(np.linspace(0.4, 6.4, 320)) + rng.normal(0, 0.1, 320), 3))
CASES = [
    {"name": "extra zero", "call": "dtw_distance([0, 1, 2, 1, 0], [0, 0, 1, 2, 1, 0])", "visible": True},
    {"name": "window 0 is the diagonal", "call": "dtw_distance([1, 5, 1], [1, 1, 5], 0)", "visible": True},
    {"name": "same series", "call": "dtw_distance([3, 1, 4, 1, 5], [3, 1, 4, 1, 5], 1)"},
    {"name": "empty", "call": "dtw_distance([], [1, 2])"},
    {"name": "length gap bigger than window", "call": "dtw_distance([1, 2, 3, 4, 5, 6], [1, 6], 1)"},
    {"name": "single values", "call": "dtw_distance([2], [7])"},
    {"name": "narrow vs wide window", "call": "dtw_distance([0, 0, 0, 9, 0, 0], [0, 9, 0, 0, 0, 0], 1)"},
    {"name": "random larger case, window 20", "call": "dtw_distance(A, B, 20)"},
    {"name": "random larger case, no window", "call": "dtw_distance(A[:150], B[:160])"},
]
