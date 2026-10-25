import numpy as np

rng = np.random.default_rng(8)
Y = rng.gamma(5.0, 10.0, size=200)
LV = [0.1, 0.25, 0.5, 0.75, 0.9]
F = np.vstack([Y * k + rng.normal(0, 3, size=200) for k in (0.7, 0.85, 1.0, 1.15, 1.3)])

CASES = [
    {"name": "median only", "call": "wql(np.array([10.0, 20.0]), np.array([[12.0, 18.0]]), [0.5])", "visible": True},
    {"name": "q=0.9 forecast too low", "call": "wql(np.array([10.0]), np.array([[5.0]]), [0.9])", "visible": True},
    {"name": "q=0.1 forecast too high", "call": "wql(np.array([10.0]), np.array([[15.0]]), [0.1])", "visible": True},
    {"name": "perfect forecast", "call": "wql(np.array([1.0, 2.0]), np.array([[1.0, 2.0], [1.0, 2.0]]), [0.1, 0.9])"},
    {"name": "all zero target", "call": "wql(np.zeros(3), np.ones((1, 3)), [0.5])"},
    {"name": "negative targets", "call": "wql(np.array([-4.0, 4.0]), np.array([[-3.0, 5.0], [-5.0, 3.0]]), [0.2, 0.8])"},
    {"name": "random gamma data, 5 levels", "call": "wql(Y, F, LV)"},
]
