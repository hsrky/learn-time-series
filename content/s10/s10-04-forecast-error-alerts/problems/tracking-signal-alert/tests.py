import numpy as np

A = [10.0, 10.0, 10.0, 10.0]
F = [8.0, 8.0, 8.0, 8.0]

rng = np.random.default_rng(21)
n = 5000
TRUTH = 100 + 10 * np.sin(np.arange(n) * 2 * np.pi / 7)
ACT = TRUTH + rng.normal(0, 4, n)
FC = TRUTH.copy()
FC[3000:] -= 3

CASES = [
    {"name": "constant bias", "call": "tracking_signal(A, F)", "visible": True, "expected": "np.array([1.0, 2.0, 3.0, 4.0])"},
    {"name": "alarm index", "call": "first_alarm(A, F, limit=3, min_periods=2)", "visible": True, "expected": "3"},
    {"name": "alternating errors, no alarm", "call": "first_alarm([5, 0, 5, 0, 5, 0, 5, 0], [0, 5, 0, 5, 0, 5, 0, 5])", "visible": True, "expected": "-1"},
    {"name": "perfect forecast gives zeros", "call": "tracking_signal([1, 2, 3], [1, 2, 3])", "expected": "np.zeros(3)"},
    {"name": "min_periods delays the alarm", "call": "first_alarm(A + [10.0] * 6, F + [8.0] * 6, limit=3, min_periods=8)", "expected": "7"},
    {"name": "negative bias", "call": "first_alarm([0] * 10, [3] * 10, limit=4, min_periods=1)", "expected": "4"},
    {"name": "single value", "call": "tracking_signal([7.0], [4.0])", "expected": "np.array([1.0])"},
    {"name": "large biased series", "call": "first_alarm(ACT, FC)"},
    {"name": "large tracking signal", "call": "tracking_signal(ACT, FC)"},
]
