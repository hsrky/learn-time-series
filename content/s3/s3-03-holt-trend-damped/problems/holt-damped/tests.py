import numpy as np

_r = np.random.default_rng(15)
LINE = (5 + 2 * np.arange(200) + _r.normal(0, 1, 200)).tolist()

CASES = [
    {"name": "lesson example", "call": "holt([10, 12, 15], 0.5, 0.5, 2)", "visible": True},
    {"name": "damped", "call": "holt([10, 12, 15], 0.5, 0.5, 2, phi=0.8)", "visible": True},
    {"name": "perfect line gives a perfect forecast", "call": "holt([1, 3, 5, 7, 9], 0.3, 0.3, 3)", "expected": "{'level': 9.0, 'trend': 2.0, 'forecast': [11.0, 13.0, 15.0]}"},
    {"name": "two points, h = 0", "call": "holt([4, 9], 0.5, 0.5, 0)", "expected": "{'level': 9.0, 'trend': 5.0, 'forecast': []}"},
    {"name": "alpha 1, beta 1", "call": "holt([2, 5, 4, 8], 1.0, 1.0, 2)"},
    {"name": "damped long horizon stays bounded", "call": "holt(LINE, 0.4, 0.1, 50, phi=0.9)"},
    {"name": "linear, 200 noisy points", "call": "holt(LINE, 0.4, 0.1, 10)"},
    {"name": "damped trend forecast is below linear", "call": "holt(LINE, 0.4, 0.1, 30, phi=0.9)['forecast'][-1] < holt(LINE, 0.4, 0.1, 30)['forecast'][-1]", "expected": "True"},
]
