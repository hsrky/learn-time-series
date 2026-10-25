import numpy as np

rng = np.random.default_rng(3)
BIG = rng.normal(20, 5, size=2000)
BIG[rng.random(2000) < 0.05] = 500.0
ORIG = np.array([1.0, 99.0, 3.0])

CASES = [
    {"name": "one spike", "call": "mask_spikes(np.array([1.0, 99.0, 3.0]), 10)", "expected": "(np.array([1.0, np.nan, 3.0]), 1)", "visible": True},
    {"name": "no spike", "call": "mask_spikes(np.array([1.0, 2.0]), 10)", "expected": "(np.array([1.0, 2.0]), 0)", "visible": True},
    {"name": "equal to limit", "call": "mask_spikes(np.array([10.0, 10.1]), 10)", "expected": "(np.array([10.0, np.nan]), 1)"},
    {"name": "existing nan", "call": "mask_spikes(np.array([np.nan, 50.0, 2.0]), 10)", "expected": "(np.array([np.nan, np.nan, 2.0]), 1)"},
    {"name": "integer input", "call": "mask_spikes(np.array([1, 200, 3]), 100)", "expected": "(np.array([1.0, np.nan, 3.0]), 1)"},
    {"name": "empty", "call": "mask_spikes(np.array([]), 10)", "expected": "(np.array([]), 0)"},
    {"name": "input unchanged", "call": "mask_spikes(ORIG, 10)\nORIG.tolist()", "expected": "[1.0, 99.0, 3.0]"},
    {"name": "random 2000", "call": "mask_spikes(BIG, 100)"},
]
