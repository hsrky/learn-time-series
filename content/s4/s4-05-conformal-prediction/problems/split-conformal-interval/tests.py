import numpy as np

rng = np.random.default_rng(13)
RES = np.abs(rng.normal(0, 4, 999))
PRED = rng.normal(100, 10, 50)

CASES = [
    {"name": "nine residuals", "call": "split_conformal([1, 2, 2, 3, 3, 4, 5, 6, 9], [100, 50], 0.2)", "visible": True,
     "expected": "(np.array([94.0, 44.0]), np.array([106.0, 56.0]))"},
    {"name": "too few residuals", "call": "split_conformal([1, 2, 3], [10], 0.1)", "visible": True,
     "expected": "(np.array([-np.inf]), np.array([np.inf]))"},
    {"name": "unsorted input", "call": "split_conformal([9, 1, 5, 3, 2, 3, 6, 4, 2], [0.0], 0.2)", "visible": True,
     "expected": "(np.array([-6.0]), np.array([6.0]))"},
    {"name": "no residuals", "call": "split_conformal([], [1.0, 2.0], 0.2)",
     "expected": "(np.array([np.nan, np.nan]), np.array([np.nan, np.nan]))"},
    {"name": "exactly enough residuals", "call": "split_conformal(list(range(1, 20)), [0.0], 0.1)",
     "expected": "(np.array([-18.0]), np.array([18.0]))"},
    {"name": "single residual, alpha 0.5", "call": "split_conformal([7.0], [1.0], 0.5)",
     "expected": "(np.array([-6.0]), np.array([8.0]))"},
    {"name": "float rank edge (n+1)*(1-alpha)=900", "call": "split_conformal(RES, PRED, 0.1)"},
    {"name": "no predictions", "call": "split_conformal([1.0, 2.0], [], 0.5)",
     "expected": "(np.array([]), np.array([]))"},
]
