import numpy as np

_r = np.random.default_rng(6)
SIM = np.where(_r.random(500) < 0.2, 1 + _r.poisson(3, 500), 0).tolist()


def err(f):
    try:
        f()
    except ValueError:
        return "ValueError"
    return "no error"


CASES = [
    {"name": "lesson example", "call": "croston([0, 0, 5, 0, 0, 0, 3, 0, 4], 0.5)", "visible": True},
    {"name": "SBA variant", "call": "croston([0, 0, 5, 0, 0, 0, 3, 0, 4], 0.5, variant='sba')", "visible": True},
    {"name": "no demand at all", "call": "croston([0, 0, 0, 0], 0.3)", "expected": "0.0"},
    {"name": "demand every period equals SES of sizes", "call": "croston([4, 4, 4, 4], 0.3)", "expected": "4.0"},
    {"name": "single demand at the start", "call": "croston([7, 0, 0, 0], 0.1)", "expected": "7.0"},
    {"name": "single demand later", "call": "croston([0, 0, 0, 6], 0.1)", "expected": "1.5"},
    {"name": "long gap keeps the forecast unchanged", "call": "croston([0, 2, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0], 0.2) == croston([0, 2, 0, 3], 0.2)", "expected": "True"},
    {"name": "simulated, 500 periods", "call": "croston(SIM, 0.1)"},
    {"name": "simulated, SBA", "call": "croston(SIM, 0.1, 'sba')"},
    {"name": "bad variant", "call": "err(lambda: croston([1, 0, 2], 0.1, 'tsb'))", "expected": "'ValueError'"},
]
