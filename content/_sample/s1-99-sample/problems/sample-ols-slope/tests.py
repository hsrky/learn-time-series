import numpy as np

CASES = [
    {"name": "line", "call": "slope([1, 3, 5, 7])", "visible": True},
    {"name": "flat", "call": "slope([2, 2, 2, 2, 2])", "visible": True},
    {"name": "noisy", "call": "slope(np.arange(30) * 0.5 + np.random.default_rng(0).normal(size=30))"},
    {"name": "down", "call": "slope([10, 8, 6, 4])"},
]
