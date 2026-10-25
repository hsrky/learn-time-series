import numpy as np
rng = np.random.default_rng(8)
LARGE = [1e9 + float(v) for v in [4, 7, 13, 16, 2, 9, 11]]
BIG = [float(v) for v in rng.normal(50, 10, 2000)]
SHIFT = [1e11 + float(v) for v in rng.normal(0, 1, 500)]
CASES = [
    {"name": "small example", "call": "r = RunningStats()\n[r.update(x) for x in [4, 8, 6]]", "visible": True},
    {"name": "single value", "call": "r = RunningStats()\nr.update(5)", "visible": True},
    {"name": "constant values", "call": "r = RunningStats()\n[r.update(3) for _ in range(4)]"},
    {"name": "negative numbers", "call": "r = RunningStats()\n[r.update(x) for x in [-2, 2, -4, 4]]"},
    {"name": "large values with tiny spread", "call": "r = RunningStats()\n[r.update(x) for x in LARGE][-1]", "tol": 1e-4},
    {"name": "random larger case", "call": "r = RunningStats()\n[r.update(x) for x in BIG][-1]", "tol": 1e-6},
    {"name": "very large offset", "call": "r = RunningStats()\n[r.update(x) for x in SHIFT][-1]", "tol": 1e-3},
]
