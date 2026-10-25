import numpy as np

_r = np.random.default_rng(1)
NOISE = _r.normal(size=500)
AR = np.zeros(500)
for _t in range(1, 500):
    AR[_t] = 0.6 * AR[_t - 1] + _r.normal()

CASES = [
    {"name": "alternating series", "call": "ljung_box([1, -1, 1, -1, 1, -1, 1, -1], 2)", "visible": True},
    {"name": "white noise, 10 lags", "call": "ljung_box(NOISE, 10, n_params=2)", "visible": True},
    {"name": "autocorrelated series has a huge Q", "call": "ljung_box(AR, 10)"},
    {"name": "constant series", "call": "ljung_box([2, 2, 2, 2, 2], 2)", "expected": "{'q': 0.0, 'df': 2}"},
    {"name": "single lag", "call": "ljung_box([3, 1, 4, 1, 5, 9, 2, 6], 1)"},
    {"name": "AR series has a much larger Q than noise", "call": "ljung_box(AR, 10)['q'] > 10 * ljung_box(NOISE, 10)['q']", "expected": "True"},
    {"name": "df uses n_params", "call": "ljung_box(NOISE, 12, n_params=3)['df']", "expected": "9"},
]
