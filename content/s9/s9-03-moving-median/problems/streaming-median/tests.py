import numpy as np
rng = np.random.default_rng(6)
BIG = [int(v) for v in rng.integers(-10**6, 10**6, 5000)]
CASES = [
    {"name": "example", "call": "m = StreamMedian()\nres = []\nfor x in [5, 15, 1, 3]:\n    m.add(x)\n    res.append(m.median())\nres", "visible": True},
    {"name": "empty", "call": "StreamMedian().median()", "visible": True},
    {"name": "duplicates", "call": "m = StreamMedian()\nres = []\nfor x in [2, 2, 2, 7, 7]:\n    m.add(x)\n    res.append(m.median())\nres"},
    {"name": "descending input", "call": "m = StreamMedian()\nres = []\nfor x in [9, 8, 7, 6, 5, 4]:\n    m.add(x)\n    res.append(m.median())\nres"},
    {"name": "negative and float", "call": "m = StreamMedian()\nres = []\nfor x in [-1.5, 2.5, -3, 0]:\n    m.add(x)\n    res.append(m.median())\nres"},
    {"name": "random larger case", "call": "m = StreamMedian()\nres = []\nfor x in BIG:\n    m.add(x)\n    res.append(m.median())\nres[::97]"},
]
