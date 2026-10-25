import numpy as np
import pandas as pd

A1 = [100, 100]
S1 = [("naive", [90, 110]), ("model", [95, 105]), ("override", [80, 120])]
A2 = [10, 20, 30, 40]
S2 = [("naive", [10, 10, 30, 30])]
S3 = [("naive", [12, 18, 33, 37]), ("stat", [11, 19, 31, 39]), ("same", [11, 19, 31, 39]), ("ml", [10, 20, 30, 40])]
rng = np.random.default_rng(8)
A4 = list(rng.integers(20, 200, 500).astype(float))
S4 = [("naive", list(np.array(A4) * rng.uniform(0.6, 1.4, 500))),
      ("stat", list(np.array(A4) * rng.uniform(0.8, 1.2, 500))),
      ("ml", list(np.array(A4) * rng.uniform(0.9, 1.1, 500))),
      ("override", list(np.array(A4) * rng.uniform(0.7, 1.3, 500)))]

CASES = [
    {"name": "example", "call": "fva_by_step(A1, S1)", "visible": True,
     "expected": "pd.DataFrame({'step': ['naive','model','override'], 'wape': [0.10, 0.05, 0.20], 'fva_prev': [0.0, 0.05, -0.15], 'fva_naive': [0.0, 0.05, -0.10], 'adds_value': [False, True, False]})"},
    {"name": "single step", "call": "fva_by_step(A2, S2)", "visible": True,
     "expected": "pd.DataFrame({'step': ['naive'], 'wape': [0.2], 'fva_prev': [0.0], 'fva_naive': [0.0], 'adds_value': [False]})"},
    {"name": "ties do not add value", "call": "fva_by_step(A2, S3)"},
    {"name": "larger random", "call": "fva_by_step(A4, S4)"},
]
