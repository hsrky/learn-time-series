import numpy as np

I1 = [{0.5: 40, 0.9: 55, 0.99: 70}, {0.5: 10, 0.9: 12, 0.99: 16}]
I2 = [{0.99: 70, 0.5: 40, 0.9: 55}]                   # unsorted keys
I3 = [{0.9: 0, 0.5: 0}, {0.5: 3}]
rng = np.random.default_rng(4)
I4 = []
for _ in range(300):
    base = float(rng.integers(5, 80))
    I4.append({0.1: base * 0.7, 0.5: base, 0.9: base * 1.3, 0.99: base * 1.8})

CASES = [
    {"name": "level 0.9", "call": "staff_levels(I1, 10, 0.9)", "expected": "[6, 2]", "visible": True},
    {"name": "interpolated 0.95", "call": "staff_levels(I1, 10, 0.95)", "expected": "[7, 2]", "visible": True},
    {"name": "above highest level uses highest", "call": "staff_levels(I1, 10, 0.999)", "expected": "[7, 2]"},
    {"name": "below lowest level uses lowest", "call": "staff_levels(I1, 10, 0.2)", "expected": "[4, 1]"},
    {"name": "unsorted dict", "call": "staff_levels(I2, 10, 0.5)", "expected": "[4]"},
    {"name": "min and max staff", "call": "staff_levels(I3 + I1, 10, 0.9, 2, 5)", "expected": "[2, 2, 5, 2]"},
    {"name": "exact multiple does not round up", "call": "staff_levels([{0.5: 20}], 10, 0.5)", "expected": "[2]"},
    {"name": "empty", "call": "staff_levels([], 10, 0.9)", "expected": "[]"},
    {"name": "larger random", "call": "staff_levels(I4, 7, 0.93, 1, 40)"},
]
