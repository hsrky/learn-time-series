import numpy as np
rng = np.random.default_rng(16)
TS = [float(v) for v in np.cumsum(rng.integers(0, 3, 4000)) * 0.25]
CASES = [
    {"name": "example", "call": "b = TokenBucket(3, 1)\n[b.allow(t) for t in [0, 0, 0, 0, 1, 1]]", "visible": True},
    {"name": "refill is capped", "call": "b = TokenBucket(2, 1)\n[b.allow(t) for t in [0, 100, 100, 100]]", "visible": True},
    {"name": "cost larger than 1", "call": "b = TokenBucket(5, 1)\n[b.allow(0, 3), b.allow(0, 3), b.allow(2, 3), b.allow(2, 1)]"},
    {"name": "rate zero never refills", "call": "b = TokenBucket(2, 0)\n[b.allow(t) for t in [0, 5, 10, 20]]"},
    {"name": "half seconds", "call": "b = TokenBucket(1, 2)\n[b.allow(t) for t in [0, 0.25, 0.5, 0.75, 1.0]]"},
    {"name": "rejected request still moves time", "call": "b = TokenBucket(1, 1)\n[b.allow(0), b.allow(0.5), b.allow(1.0)]"},
    {"name": "random larger case", "call": "b = TokenBucket(5, 2)\nsum(b.allow(t) for t in TS)"},
]
