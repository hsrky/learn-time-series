import numpy as np
rng = np.random.default_rng(22)
users = ["u%d" % i for i in rng.integers(0, 50, 20000)]
times = [int(v) for v in rng.integers(0, 2_000_000, 20000)]
BIG = list(zip(users, times))
CASES = [
    {"name": "two users", "call": "sessionize([('ann', 0), ('ann', 300), ('ann', 4200), ('bob', 100)])", "visible": True},
    {"name": "empty", "call": "sessionize([])", "visible": True},
    {"name": "gap exactly 1800", "call": "sessionize([('a', 0), ('a', 1800), ('a', 3601)])"},
    {"name": "unsorted input", "call": "sessionize([('a', 5000), ('a', 10), ('b', 20), ('a', 4000)])"},
    {"name": "duplicates", "call": "sessionize([('a', 5), ('a', 5), ('a', 5)])"},
    {"name": "user change at a small gap", "call": "sessionize([('a', 100), ('b', 101)])"},
    {"name": "random larger case", "call": "sessionize(BIG)[:40]"},
    {"name": "random larger case (count)", "call": "len(sessionize(BIG))"},
]
