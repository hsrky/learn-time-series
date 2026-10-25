import numpy as np

_r = np.random.default_rng(16)
SIM = np.where(_r.random(300) < 0.3, 1 + _r.poisson(4, 300), 0).tolist()
STOPPED = SIM[:150] + [0] * 150

CASES = [
    {"name": "lesson example", "call": "tsb([0, 0, 5, 0, 0, 0, 3, 0, 4], 0.5, 0.2)", "visible": True},
    {"name": "zeros after sales", "call": "tsb([3, 3, 3, 0, 0, 0, 0], 0.5, 0.5)", "visible": True},
    {"name": "no demand", "call": "tsb([0, 0, 0], 0.3, 0.3)", "expected": "0.0"},
    {"name": "path length and zeros before the first demand", "call": "tsb_path([0, 0, 4, 0], 0.5, 0.5)", "expected": "[0.0, 0.0, 4.0 / 3, 2.0 / 3]"},
    {"name": "path last value equals tsb", "call": "tsb_path(SIM, 0.1, 0.1)[-1] == tsb(SIM, 0.1, 0.1)", "expected": "True"},
    {"name": "simulated demand", "call": "tsb(SIM, 0.1, 0.1)"},
    {"name": "obsolete item: forecast near zero", "call": "tsb(STOPPED, 0.1, 0.1) < 0.01", "expected": "True"},
    {"name": "path for a short series", "call": "tsb_path([2, 0, 0, 5, 0], 0.3, 0.4)"},
]
