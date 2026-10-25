import numpy as np

W = np.zeros((5, 2)); W[-1, :] = 1.0
X1 = np.array([[1.0, 2, 3, 4, 5]])
rng = np.random.default_rng(9)
XB = rng.normal(size=(16, 96)).cumsum(axis=1)
WT = rng.normal(size=(96, 24)) * 0.05
WR = rng.normal(size=(96, 24)) * 0.05

CASES = [
    {"name": "copy last step", "call": "dlinear_forward(X1, W, W, 3)", "visible": True},
    {"name": "kernel 1: trend is x", "call": "dlinear_forward(X1, W, np.zeros((5, 2)), 1)", "visible": True},
    {"name": "two rows", "call": "dlinear_forward(np.array([[1.0,1,1,1,1],[0,1,0,1,0]]), W, W, 5)", "visible": True},
    {"name": "constant series", "call": "dlinear_forward(np.full((1, 5), 4.0), np.ones((5, 3)) / 5, np.ones((5, 3)), 3)"},
    {"name": "empty batch", "call": "dlinear_forward(np.zeros((0, 5)), W, W, 3)"},
    {"name": "random walk batch, kernel 25", "call": "dlinear_forward(XB, WT, WR, 25)"},
    {"name": "kernel equals L", "call": "dlinear_forward(XB, WT, WR, 95)"},
]
