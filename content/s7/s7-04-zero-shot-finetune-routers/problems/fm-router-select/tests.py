import numpy as np

rng = np.random.default_rng(17)
# 6 models with equal true quality: validation differences are pure noise
TRUE = rng.uniform(1, 2, size=300)
VAL = TRUE[None, :] * rng.lognormal(0, 0.3, size=(6, 300))
TST = TRUE[None, :] * rng.lognormal(0, 0.3, size=(6, 300))
# 3 models where model 2 is truly better on half of the series
V2 = np.vstack([np.ones(100), np.ones(100) * 1.2, np.r_[np.full(50, 0.6), np.full(50, 1.5)]])

CASES = [
    {"name": "tiny example", "call": "route(np.array([[1, 5], [2, 1]]), np.array([[1, 5], [2, 1]]))", "visible": True},
    {"name": "router beats global", "call": "route(V2, V2)", "visible": True},
    {"name": "ties choose lowest index", "call": "route(np.ones((3, 4)), np.arange(12.0).reshape(3, 4))", "visible": True},
    {"name": "single model", "call": "route(np.array([[1.0, 2.0, 3.0]]), np.array([[2.0, 2.0, 2.0]]))"},
    {"name": "no series", "call": "route(np.zeros((3, 0)), np.zeros((3, 0)))"},
    {"name": "noise only: router wins on val, not on test", "call": "route(VAL, TST)"},
]
