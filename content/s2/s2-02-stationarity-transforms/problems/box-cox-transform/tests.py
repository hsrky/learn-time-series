import numpy as np

rng = np.random.default_rng(11)
BIG = rng.uniform(0.5, 500, 2000)


def err(f):
    try:
        f()
    except ValueError:
        return "ValueError"
    return "no error"


CASES = [
    {"name": "lambda 0.5", "call": "box_cox([1, 4, 9], 0.5)", "visible": True},
    {"name": "lambda 0 is log", "call": "box_cox([1, np.e], 0)", "visible": True},
    {"name": "lambda 1 shifts by one", "call": "box_cox([5, 10], 1)", "expected": "np.array([4.0, 9.0])"},
    {"name": "negative lambda", "call": "box_cox([2, 8], -1)", "expected": "np.array([0.5, 0.875])"},
    {"name": "inverse lambda 0.5", "call": "inv_box_cox([0, 2, 4], 0.5)", "expected": "np.array([1.0, 4.0, 9.0])"},
    {"name": "inverse lambda 0", "call": "inv_box_cox([0, 1], 0)", "expected": "np.array([1.0, np.e])"},
    {"name": "zero raises", "call": "err(lambda: box_cox([1, 0, 2], 0.3))", "expected": "'ValueError'"},
    {"name": "round trip on 2000 values", "call": "inv_box_cox(box_cox(BIG, 0.3), 0.3)", "expected": "BIG", "tol": 1e-8},
]
