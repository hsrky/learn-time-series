import numpy as np
rng = np.random.default_rng(9)
BIG = [int(v) for v in rng.integers(-1000, 1000, 20000)]
DUP = [int(v) for v in rng.integers(0, 4, 3000)]
CASES = [
    {"name": "example", "call": "m = MovingMedian(3)\n[m.next(x) for x in [1, 3, -1, -3, 5, 3]]", "visible": True},
    {"name": "k = 1", "call": "m = MovingMedian(1)\n[m.next(x) for x in [4, 9, 2]]", "visible": True},
    {"name": "even window", "call": "m = MovingMedian(4)\n[m.next(x) for x in [1, 2, 3, 4, 5, 6]]"},
    {"name": "k larger than input", "call": "m = MovingMedian(10)\n[m.next(x) for x in [5, 1, 9]]"},
    {"name": "spike is ignored", "call": "m = MovingMedian(5)\n[m.next(x) for x in [10, 11, 10, 9000, 10, 11, 10, 10]]"},
    {"name": "many duplicates", "call": "m = MovingMedian(7)\n[m.next(x) for x in DUP][::31]"},
    {"name": "random larger case, k = 1000", "call": "m = MovingMedian(1000)\n[m.next(x) for x in BIG][::211]"},
]
