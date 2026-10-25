import numpy as np

_r = np.random.default_rng(10)
BASE = _r.normal(size=400)
Y_LAG4 = np.concatenate([_r.normal(size=4), BASE[:-4]]) + _r.normal(0, 0.3, 400)      # x leads y by 4
X_LAG4 = np.concatenate([BASE[7:], _r.normal(size=7)]) + _r.normal(0, 0.3, 400)       # X leads BASE by 7
_w1 = np.cumsum(_r.normal(size=300))
_w2 = np.cumsum(_r.normal(size=300))

CASES = [
    {"name": "x leads y by 2", "call": "best_lead_lag([1, 3, 2, 5, 4, 6], [0, 0, 1, 3, 2, 5], 2, difference=False)", "visible": True},
    {"name": "lag zero only", "call": "best_lead_lag([1, 3, 2, 5, 4, 6], [0, 0, 1, 3, 2, 5], 0, difference=False)", "visible": True},
    {"name": "y leads x (negative lag)", "call": "best_lead_lag([0, 0, 1, 3, 2, 5], [1, 3, 2, 5, 4, 6], 2, difference=False)"},
    {"name": "negative correlation wins", "call": "best_lead_lag([1, 2, 3, 4, 5, 6], [6, 5, 4, 3, 2, 1], 1, difference=False)"},
    {"name": "constant series", "call": "best_lead_lag([2, 2, 2, 2, 2], [1, 2, 3, 4, 5], 1, difference=False)", "expected": "{'lag': 0, 'corr': 0.0}"},
    {"name": "noisy, x leads y by 4, 400 points", "call": "best_lead_lag(BASE, Y_LAG4, 10)"},
    {"name": "noisy, expected lag", "call": "best_lead_lag(BASE, Y_LAG4, 10)['lag']", "expected": "4"},
    {"name": "y leads x by 7 (negative lag)", "call": "best_lead_lag(BASE, X_LAG4, 10)['lag']", "expected": "-7"},
    {"name": "independent random walks, differenced", "call": "best_lead_lag(_w1, _w2, 5)"},
]
