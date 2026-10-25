import numpy as np

rng = np.random.default_rng(12)
XB = rng.normal(size=(10, 12))
BL = [(rng.normal(size=(12, 12)) * 0.3, rng.normal(size=(12, 4)) * 0.3) for _ in range(5)]

def check(got, exp, case):
    if exp[0] is None:
        return (got[0] is None and np.allclose(got[1], exp[1])), "expected (None, x)"
    if got[0] is None:
        return False, "forecast is None"
    ok = np.allclose(got[0], exp[0]) and np.allclose(got[1], exp[1]) and got[0].shape == exp[0].shape
    return bool(ok), "forecast or residual differs"

CASES = [
    {"name": "one block explains everything", "call": "nbeats_forward(np.array([[1.0, 2.0]]), [(np.eye(2), np.array([[1.0], [1.0]]))])", "visible": True},
    {"name": "two blocks", "call": "nbeats_forward(np.array([[1.0, 2.0]]), [(np.eye(2) * 0.5, np.array([[1.0], [0.0]])), (np.eye(2), np.array([[0.0], [1.0]]))])", "visible": True},
    {"name": "no blocks", "call": "nbeats_forward(np.array([[1.0, 2.0]]), [])", "visible": True},
    {"name": "empty batch", "call": "nbeats_forward(np.zeros((0, 3)), [(np.eye(3), np.ones((3, 2)))])"},
    {"name": "zero backcast keeps the input", "call": "nbeats_forward(np.array([[1.0, 2.0, 3.0]]), [(np.zeros((3, 3)), np.ones((3, 2))), (np.zeros((3, 3)), np.ones((3, 2)))])"},
    {"name": "5 random blocks, batch 10", "call": "nbeats_forward(XB, BL)"},
]
