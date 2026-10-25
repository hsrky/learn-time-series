import numpy as np
rng = np.random.default_rng(21)
BIG = list(np.round(np.concatenate([rng.normal(10, 1, 300), rng.normal(12, 1, 300), rng.normal(8, 1, 300)]), 3))
CASES = [
    {"name": "up then down", "call": "cusum_detect([10, 11, 12, 12, 9, 8, 7], 10, 0.5, 3)", "visible": True},
    {"name": "no change", "call": "cusum_detect([5, 5, 5], 5, 0.5, 1)", "visible": True},
    {"name": "empty", "call": "cusum_detect([], 0, 0.5, 3)"},
    {"name": "single huge value", "call": "cusum_detect([0, 0, 50, 0, 0], 0, 1, 10)"},
    {"name": "slow drift inside the slack", "call": "cusum_detect([10.4, 10.3, 10.4, 10.2, 10.4, 10.3], 10, 0.5, 1)"},
    {"name": "repeated alarms", "call": "cusum_detect([5] * 12, 0, 1, 6)"},
    {"name": "random larger case", "call": "cusum_detect(BIG, 10, 0.5, 5)"},
]
