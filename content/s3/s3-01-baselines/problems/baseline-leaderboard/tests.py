import numpy as np

_r = np.random.default_rng(12)
_t = np.arange(200)
SIG = 100 + 0.2 * _t + 10 * np.sin(2 * np.pi * _t / 7) + _r.normal(0, 2, 200)


def check(got, exp, case):
    if not isinstance(exp, dict):
        return got == exp, "" if got == exp else f"expected {exp}"
    if got["best"] != exp["best"] or abs(got["skill"] - exp["skill"]) > 1e-3 or set(got["mae"]) != set(exp["mae"]):
        return False, f"expected {exp}"
    ok = all(abs(got["mae"][k] - exp["mae"][k]) <= 1e-3 for k in exp["mae"])
    return ok, "" if ok else f"expected {exp}"


CASES = [
    {"name": "seasonal data", "call": "leaderboard([10, 20, 30, 40, 12, 22, 32, 42], [14, 24, 34, 44], 4)", "visible": True},
    {"name": "perfect line", "call": "leaderboard([1, 2, 3, 4, 5], [6, 7], 1)", "visible": True},
    {"name": "constant series: tie goes to first method", "call": "leaderboard([5, 5, 5, 5], [5, 5], 2)"},
    {"name": "season longer than train is skipped", "call": "leaderboard([1, 3, 2], [4, 5], 5)"},
    {"name": "noisy weekly data", "call": "leaderboard(SIG[:170], SIG[170:], 7)"},
    {"name": "noisy weekly data, best method", "call": "leaderboard(SIG[:170], SIG[170:], 7)['best']", "expected": "'seasonal_naive'"},
    {"name": "wrong season length is worse", "call": "leaderboard(SIG[:170], SIG[170:], 5)"},
]
