import numpy as np

_r = np.random.default_rng(2)
SERIES = np.cumsum(np.cumsum(_r.normal(size=60)))
D2 = np.diff(SERIES, n=2)


def err(f):
    try:
        f()
    except ValueError:
        return "ValueError"
    return "no error"


CASES = [
    {"name": "second differences of squares", "call": "integrate_forecast([1, 4, 9, 16], [2, 2, 2], 2)", "visible": True},
    {"name": "first difference", "call": "integrate_forecast([100], [2, 1.6, 1.28], 1)", "visible": True},
    {"name": "d = 0 returns the input", "call": "integrate_forecast([5, 6], [1.5, 2.5], 0)", "expected": "np.array([1.5, 2.5])"},
    {"name": "empty forecast", "call": "integrate_forecast([1, 2, 3], [], 1)", "expected": "np.array([])"},
    {"name": "d = 3 on cubes", "call": "integrate_forecast([1, 8, 27, 64, 125], [6, 6], 3)", "expected": "np.array([216.0, 343.0])"},
    {"name": "round trip: history is its own future (d=1)", "call": "integrate_forecast(SERIES[:-5], np.diff(SERIES)[-5:], 1)", "expected": "SERIES[-5:]", "tol": 1e-9},
    {"name": "round trip (d=2)", "call": "integrate_forecast(SERIES[:-5], D2[-5:], 2)", "expected": "SERIES[-5:]", "tol": 1e-9},
    {"name": "not enough history", "call": "err(lambda: integrate_forecast([3], [1], 2))", "expected": "'ValueError'"},
]
