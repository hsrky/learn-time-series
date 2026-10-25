import numpy as np

_r = np.random.default_rng(4)
STEP = (np.concatenate([np.full(50, 100.0), np.full(50, 120.0)]) + _r.normal(0, 3, 100)).tolist()
NOISE = (80 + _r.normal(0, 5, 300)).tolist()
GRID = [round(a, 2) for a in np.arange(0.05, 1.0001, 0.05)]

CASES = [
    {"name": "lesson series", "call": "fit_ses_alpha([10, 14, 12, 16], [0.25, 0.5, 0.75, 1.0])", "visible": True},
    {"name": "constant series: tie goes to smaller alpha", "call": "fit_ses_alpha([5, 5, 5, 5], [0.9, 0.1])", "visible": True},
    {"name": "two points", "call": "fit_ses_alpha([3, 7], [0.2, 0.6])"},
    {"name": "level shift prefers a large alpha", "call": "fit_ses_alpha(STEP, GRID)"},
    {"name": "noise around a fixed level prefers a small alpha", "call": "fit_ses_alpha(NOISE, GRID)"},
    {"name": "noise: alpha is small", "call": "fit_ses_alpha(NOISE, GRID)['alpha'] <= 0.15", "expected": "True"},
    {"name": "single-element grid", "call": "fit_ses_alpha(STEP, [0.3])"},
]
