import numpy as np

def naive(train, h):
    return np.full(h, train[-1])

def drift(train, h):
    slope = (train[-1] - train[0]) / (len(train) - 1)
    return train[-1] + slope * np.arange(1, h + 1)

def seasonal_naive(train, h, m=7):
    return np.array([train[-m + (i % m)] for i in range(h)])

def spy(train, h):
    # forecast the training mean (the training part grows with each fold)
    return np.full(h, train.mean())

rng = np.random.default_rng(3)
T = np.arange(210)
Y = 20 + 5 * np.sin(2 * np.pi * T / 7) + 0.05 * T + rng.normal(0, 0.5, 210)
L = np.array([1.0, 2, 3, 4, 5, 6])

CASES = [
    {"name": "naive on a line", "call": "walk_forward_mae(L, naive, 3, 2)", "visible": True,
     "expected": "np.array([1.0, 2.0])"},
    {"name": "drift is exact on a line", "call": "walk_forward_mae(L, drift, 3, 2)", "visible": True,
     "expected": "np.array([0.0, 0.0])"},
    {"name": "step 2 skips origins", "call": "walk_forward_mae(np.array([1.0, 2, 4, 8, 16, 32, 64]), naive, 2, 2, step=2)", "visible": True,
     "expected": "np.array([5.0, 15.0])"},
    {"name": "no fold fits", "call": "walk_forward_mae(L, naive, 6, 2)", "expected": "np.array([np.nan, np.nan])"},
    {"name": "horizon 1", "call": "walk_forward_mae(L, naive, 5, 1)", "expected": "np.array([1.0])"},
    {"name": "seasonal naive on seasonal data", "call": "walk_forward_mae(Y, seasonal_naive, 70, 3, step=7)"},
    {"name": "naive grows with horizon", "call": "walk_forward_mae(Y, naive, 70, 7, step=1)"},
    {"name": "training part grows (mean forecaster)", "call": "walk_forward_mae(Y, spy, 50, 5, step=3)"},
]
