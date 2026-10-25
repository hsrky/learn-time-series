import numpy as np
rng = np.random.default_rng(26)
_n = 5000
BX = list(range(_n))
BY = list(np.sin(np.arange(_n) / 40) * 10 + rng.normal(0, 1, _n))
BY[2500] += 50
CASES = [
    {"name": "spike survives", "call": "lttb(list(range(10)), [0, 1, 0, 1, 0, 9, 0, 1, 0, 1], 5)", "visible": True},
    {"name": "threshold larger than n", "call": "lttb([0, 1, 2], [5, 6, 7], 10)", "visible": True},
    {"name": "threshold 2", "call": "lttb([0, 1, 2, 3], [5, 6, 7, 1], 2)"},
    {"name": "threshold 3 keeps one middle point", "call": "lttb(list(range(7)), [0, 0, 5, 0, 0, 0, 0], 3)"},
    {"name": "single point", "call": "lttb([0], [1], 5)"},
    {"name": "uneven x", "call": "lttb([0, 1, 3, 4, 8, 9, 12, 13, 14, 20], [1, 3, 2, 8, 1, 1, 6, 2, 9, 0], 6)"},
    {"name": "random larger case", "call": "lttb(BX, BY, 200)"},
]
