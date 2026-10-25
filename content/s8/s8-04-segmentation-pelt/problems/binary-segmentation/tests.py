import numpy as np
rng = np.random.default_rng(31)
BIG = list(np.round(np.concatenate([rng.normal(0, 1, 200), rng.normal(6, 1, 150), rng.normal(-3, 1, 250)]), 3))
NOISE = list(np.round(rng.normal(0, 1, 300), 3))
CASES = [
    {"name": "one shift", "call": "binary_segmentation([1, 1, 1, 1, 5, 5, 5, 5], 2, 5)", "visible": True},
    {"name": "two shifts", "call": "binary_segmentation([1, 1, 1, 1, 5, 5, 5, 5, 9, 9, 9, 9], 2, 5)", "visible": True},
    {"name": "flat series", "call": "binary_segmentation([3, 3, 3, 3, 3, 3], 1, 0)"},
    {"name": "too short for min_size", "call": "binary_segmentation([1, 9, 1], 2, 0)"},
    {"name": "empty", "call": "binary_segmentation([], 1, 1)"},
    {"name": "big penalty blocks cuts", "call": "binary_segmentation([1, 1, 1, 5, 5, 5], 1, 1000)"},
    {"name": "pure noise with a sensible penalty", "call": "binary_segmentation(NOISE, 10, 30)"},
    {"name": "random larger case (3 levels)", "call": "binary_segmentation(BIG, 10, 30)"},
]
