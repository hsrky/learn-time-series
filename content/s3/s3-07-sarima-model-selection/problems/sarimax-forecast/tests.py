import numpy as np

_r = np.random.default_rng(10)
_n = 60
_t = np.arange(_n)
Y = (50 + 0.1 * _t + 8 * np.sin(2 * np.pi * _t / 4) + _r.normal(0, 2, _n)).tolist()
CANDS = [((1, 1, 0), (1, 1, 0, 4)), ((0, 1, 1), (0, 1, 1, 4))]


def check(got, exp, case):
    if not isinstance(exp, dict):
        return got == exp, "" if got == exp else f"expected {exp}"
    if got["best"] != exp["best"] or abs(got["aic"] - exp["aic"]) > 0.5:
        return False, f"expected best={exp['best']} aic={exp['aic']}, got best={got['best']} aic={got['aic']}"
    ok = len(got["forecast"]) == len(exp["forecast"]) and all(abs(a - b) <= 0.05 for a, b in zip(got["forecast"], exp["forecast"]))
    return ok, "" if ok else "forecast values differ"


CASES = [
    {"name": "two candidates with the same d and D", "call": "best_sarimax(Y, CANDS, 8)", "visible": True},
    {"name": "seasonal naive", "call": "seasonal_naive([1, 2, 3, 4], 2, 5)", "expected": "[3.0, 4.0, 3.0, 4.0, 3.0]", "visible": True},
    {"name": "single candidate", "call": "best_sarimax(Y, CANDS[1:], 3)"},
    {"name": "forecast length", "call": "len(best_sarimax(Y, CANDS[1:], 10)['forecast'])", "expected": "10"},
    {"name": "tie goes to the lowest index", "call": "best_sarimax(Y, [CANDS[0], CANDS[0]], 2)['best']", "expected": "0"},
    {"name": "model beats seasonal naive on a hold-out", "call": "float(np.mean(np.abs(np.array(Y[-4:]) - np.array(best_sarimax(Y[:-4], CANDS[1:], 4)['forecast'])))) < float(np.mean(np.abs(np.array(Y[-4:]) - np.array(seasonal_naive(Y[:-4], 4, 4)))))", "expected": "True"},
]
