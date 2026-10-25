import numpy as np
rng = np.random.default_rng(15)
BIG = [float(v) for v in rng.normal(10, 3, 3000)]
CASES = [
    {"name": "simple", "call": "e = StreamingEWMA(0.5)\n[e.update(x) for x in [10, 20, 30]]", "visible": True},
    {"name": "alpha 1 follows the data", "call": "e = StreamingEWMA(1.0)\n[e.update(x) for x in [3, 9, 4]]", "visible": True},
    {"name": "single value", "call": "StreamingEWMA(0.1).update(7)"},
    {"name": "constant series", "call": "e = StreamingEWMA(0.3)\n[e.update(5) for _ in range(5)]"},
    {"name": "irregular times", "call": "e = StreamingEWMA(0.5)\n[e.update_at(x, t, 10) for x, t in [(10, 0), (20, 5), (30, 25), (0, 26)]]"},
    {"name": "random larger case", "call": "e = StreamingEWMA(0.05)\n[e.update(x) for x in BIG][-5:]"},
]
