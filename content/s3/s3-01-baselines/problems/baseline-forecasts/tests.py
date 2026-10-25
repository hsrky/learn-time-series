import numpy as np

_r = np.random.default_rng(6)
BIG = 20 + 0.1 * np.arange(500) + 5 * np.sin(2 * np.pi * np.arange(500) / 12) + _r.normal(0, 1, 500)


def err(f):
    try:
        f()
    except ValueError:
        return "ValueError"
    return "no error"


CASES = [
    {"name": "drift example", "call": "baseline_forecast([10, 12, 14, 13], 3, 'drift')", "visible": True},
    {"name": "seasonal naive example", "call": "baseline_forecast([10, 20, 30, 40, 12, 22, 32, 42], 6, 'seasonal_naive', m=4)", "visible": True},
    {"name": "mean", "call": "baseline_forecast([1, 2, 3, 6], 2, 'mean')", "expected": "np.array([3.0, 3.0])"},
    {"name": "naive", "call": "baseline_forecast([1, 2, 3, 6], 3, 'naive')", "expected": "np.array([6.0, 6.0, 6.0])"},
    {"name": "single point drift", "call": "baseline_forecast([5], 3, 'drift')", "expected": "np.array([5.0, 5.0, 5.0])"},
    {"name": "season length 1 equals naive", "call": "baseline_forecast([3, 9, 4], 2, 'seasonal_naive', m=1)", "expected": "np.array([4.0, 4.0])"},
    {"name": "unknown method", "call": "err(lambda: baseline_forecast([1, 2], 1, 'median'))", "expected": "'ValueError'"},
    {"name": "season longer than data", "call": "err(lambda: baseline_forecast([1, 2], 1, 'seasonal_naive', m=3))", "expected": "'ValueError'"},
    {"name": "large series, m=12, h=30", "call": "baseline_forecast(BIG, 30, 'seasonal_naive', m=12)"},
    {"name": "large series drift", "call": "baseline_forecast(BIG, 30, 'drift')"},
]
