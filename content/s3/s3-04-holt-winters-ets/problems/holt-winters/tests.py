import numpy as np

_t = np.arange(48)
CLEAN_ADD = (20 + 0.5 * _t + 5 * np.sin(2 * np.pi * _t / 12)).tolist()
CLEAN_MUL = ((20 + 0.5 * _t) * (1 + 0.25 * np.sin(2 * np.pi * _t / 12))).tolist()
_r = np.random.default_rng(33)
_tt = np.arange(364)
NOISY = (100 + 0.1 * _tt + 12 * np.sin(2 * np.pi * _tt / 7) + _r.normal(0, 2, 364)).tolist()


def err(f):
    try:
        f()
    except ValueError:
        return "ValueError"
    return "no error"


CASES = [
    {"name": "small additive example", "call": "holt_winters([10, 20, 30, 40, 12, 22, 32, 42], 4, 0.5, 0.5, 0.5, 4)", "visible": True},
    {"name": "clean additive series", "call": "holt_winters(CLEAN_ADD, 12, 0.3, 0.1, 0.2, 12)", "visible": True},
    {"name": "clean multiplicative series", "call": "holt_winters(CLEAN_MUL, 12, 0.3, 0.1, 0.2, 12, seasonal='mul')"},
    {"name": "noisy weekly data", "call": "holt_winters(NOISY, 7, 0.2, 0.05, 0.1, 14)"},
    {"name": "noisy weekly data, multiplicative", "call": "holt_winters(NOISY, 7, 0.2, 0.05, 0.1, 14, seasonal='mul')"},
    {"name": "h = 0", "call": "holt_winters(CLEAN_ADD, 12, 0.3, 0.1, 0.2, 0)"},
    {"name": "exactly two seasons", "call": "holt_winters([5, 9, 6, 10, 7, 11], 3, 0.4, 0.2, 0.3, 3)"},
    {"name": "too short", "call": "err(lambda: holt_winters([1, 2, 3, 4, 5], 3, 0.5, 0.5, 0.5, 2))", "expected": "'ValueError'"},
]
