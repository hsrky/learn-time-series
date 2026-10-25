import numpy as np
rng = np.random.default_rng(20)
BIG = [int(v) for v in rng.integers(0, 3_000_000, 50000)]
CASES = [
    {"name": "example", "call": "bucket_counts([5, 61, 62, 200], 60)", "visible": True},
    {"name": "empty", "call": "bucket_counts([], 60)", "visible": True},
    {"name": "single event", "call": "bucket_counts([125], 60)"},
    {"name": "unsorted and boundary values", "call": "bucket_counts([120, 59, 60, 0, 119], 60)"},
    {"name": "size 1", "call": "bucket_counts([3, 1, 1], 1)"},
    {"name": "large gap", "call": "bucket_counts([0, 100000], 10000)"},
    {"name": "random larger case", "call": "bucket_counts(BIG, 3600)[::7]"},
]
