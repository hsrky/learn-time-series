import numpy as np

rng = np.random.default_rng(0)
E = rng.normal(size=300)
WALK = np.cumsum(E)
AR = np.zeros(300)
for _t in range(1, 300):
    AR[_t] = 0.5 * AR[_t - 1] + E[_t]
NOISE = np.random.default_rng(4).normal(size=200)
I2 = np.cumsum(np.cumsum(np.random.default_rng(9).normal(size=300)))


def check(got, exp, case):
    if isinstance(exp, dict):
        ok = got.get("verdict") == exp["verdict"] and all(abs(got[k] - exp[k]) <= 2e-4 for k in ("adf_p", "kpss_p"))
        return ok, "" if ok else f"expected {exp}"
    return got == exp, "" if got == exp else f"expected {exp}"


CASES = [
    {"name": "random walk", "call": "unit_root_verdict(WALK)", "visible": True},
    {"name": "AR(1) phi 0.5", "call": "unit_root_verdict(AR)", "visible": True},
    {"name": "white noise", "call": "unit_root_verdict(NOISE)"},
    {"name": "differenced walk", "call": "unit_root_verdict(np.diff(WALK))"},
    {"name": "d for random walk", "call": "suggest_d(WALK)", "expected": "1"},
    {"name": "d for stationary series", "call": "suggest_d(AR)", "expected": "0"},
    {"name": "d for double-integrated series", "call": "suggest_d(I2)", "expected": "2"},
    {"name": "very strict alpha: KPSS p 0.01 no longer rejects", "call": "unit_root_verdict(WALK, alpha=0.001)['verdict']", "expected": "'inconclusive'"},
]
