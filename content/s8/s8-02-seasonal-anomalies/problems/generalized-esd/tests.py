import numpy as np
rng = np.random.default_rng(11)
BIG = list(rng.normal(100, 5, 300))
BIG[20] = 150; BIG[21] = 152; BIG[200] = 60
CASES = [
    {"name": "one clear outlier", "call": "generalized_esd([10, 11, 9, 10, 12, 10, 11, 9, 10, 40], 3)", "visible": True},
    {"name": "flat data", "call": "generalized_esd([5, 5, 5, 5], 2)", "visible": True},
    {"name": "no outlier", "call": "generalized_esd([10, 11, 9, 10, 12, 10, 11, 9, 10, 11], 3)"},
    {"name": "two outliers", "call": "generalized_esd([10, 11, 9, 10, 12, 10, 11, 9, 10, 11, 10, 9, 11, 10, 60, -40], 4)"},
    {"name": "r larger than needed", "call": "generalized_esd([1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 30], 8, 0.01)"},
    {"name": "tiny sample", "call": "generalized_esd([1, 2, 100], 3)"},
    {"name": "random larger case with a masked pair", "call": "generalized_esd(BIG, 10)"},
]
