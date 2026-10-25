import numpy as np

_r = np.random.default_rng(5)
HIST = _r.uniform(5, 50, size=(200, 6))
TF = _r.uniform(100, 200, size=10).tolist()


def err(f):
    try:
        f()
    except ValueError:
        return "ValueError"
    return "no error"


CASES = [
    {"name": "proportion of averages", "call": "top_down([[30, 20], [40, 20]], [66], 'prop_of_avgs')", "visible": True},
    {"name": "average of proportions", "call": "top_down([[30, 20], [40, 20]], [60, 70])", "visible": True},
    {"name": "single bottom series gets the whole total", "call": "top_down([[5], [6]], [10, 20])", "expected": "np.array([[10.0], [20.0]])"},
    {"name": "h = 0", "call": "top_down([[1, 2]], [], 'prop_of_avgs').shape", "expected": "(0, 2)"},
    {"name": "random history, avg of props", "call": "top_down(HIST, TF)"},
    {"name": "random history, prop of avgs", "call": "top_down(HIST, TF, 'prop_of_avgs')"},
    {"name": "rows sum to the total forecast", "call": "np.allclose(top_down(HIST, TF).sum(axis=1), TF)", "expected": "True"},
    {"name": "unknown method", "call": "err(lambda: top_down([[1, 2]], [3], 'median'))", "expected": "'ValueError'"},
]
