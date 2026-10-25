import numpy as np
rng = np.random.default_rng(4)
BIG = rng.normal(0, 1, 3000)
Q = np.sin(np.linspace(0, 3, 25)) * 5 + 100
BIG[1234:1259] = Q * 0.3 + 7 + rng.normal(0, 0.02, 25)
BIG = list(BIG)
Q = list(Q)
CASES = [
    {"name": "same shape at the start", "call": "best_match([0, 1, 0, 5, 10, 5, 0, 1, 0], [1, 2, 1])", "visible": True},
    {"name": "tie goes to the smaller start", "call": "best_match([3, 1, 2, 4, 6, 8, 2], [10, 20, 30])", "visible": True},
    {"name": "query as long as the series", "call": "best_match([1, 2, 3, 2], [5, 6, 7, 6])"},
    {"name": "flat query", "call": "best_match([4, 4, 4, 1, 9], [2, 2, 2])"},
    {"name": "downward shape", "call": "best_match([1, 2, 3, 9, 7, 5, 3], [10, 8, 6])"},
    {"name": "random larger case (hidden scaled copy)", "call": "best_match(BIG, Q)"},
]
