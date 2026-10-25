import numpy as np

HIST = [3.0, 1.0, 4.0, 1.0, 5.0, 9.0, 2.0, 6.0]
ORIG = list(HIST)


def err(f):
    try:
        f()
    except ValueError:
        return "ValueError"
    return "no error"


CASES = [
    {"name": "stays at the mean", "call": "ar_forecast([8, 9, 10], [2.0, 0.8], 3)", "visible": True},
    {"name": "decays to the mean", "call": "ar_forecast([15], [2.0, 0.8], 3)", "visible": True},
    {"name": "AR(2) uses lag order", "call": "ar_forecast([1.0, 2.0], [0.0, 0.5, 0.25], 3)", "expected": "np.array([1.25, 1.125, 0.875])"},
    {"name": "h = 0", "call": "ar_forecast([1, 2, 3], [0.5, 0.5], 0)", "expected": "np.array([])"},
    {"name": "AR(3) long horizon", "call": "ar_forecast(HIST, [1.0, 0.4, 0.2, 0.1], 40)"},
    {"name": "input is not modified", "call": "(ar_forecast(HIST, [1.0, 0.4, 0.2], 5), HIST == ORIG)[1]", "expected": "True"},
    {"name": "history too short", "call": "err(lambda: ar_forecast([1.0], [0, 0.5, 0.2], 2))", "expected": "'ValueError'"},
    {"name": "random walk coefficients (phi = 1) stay flat", "call": "ar_forecast([4, 7], [0.0, 1.0], 4)", "expected": "np.array([7.0, 7.0, 7.0, 7.0])"},
]
