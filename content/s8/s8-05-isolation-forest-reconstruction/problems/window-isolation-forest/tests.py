import numpy as np
rng = np.random.default_rng(0)
_t = np.arange(120)
DEMO = list(np.round(np.sin(2 * np.pi * _t / 12) + rng.normal(0, 0.05, 120), 4))
for _i in range(70, 82):
    DEMO[_i] = 0.0
_t2 = np.arange(600)
BIG = np.sin(2 * np.pi * _t2 / 30) + rng.normal(0, 0.1, 600)
BIG[400:420] += 3.0
BIG = list(BIG)

def check(got, exp, case):
    if not isinstance(got, (list, tuple)) or len(got) != len(exp):
        return False, "expected a list of %d start positions" % len(exp)
    ok = sorted(int(g) for g in got) == list(exp)
    return ok, "" if ok else "different windows than the reference (check features, settings and the sort direction)"

CASES = [
    {"name": "flat piece in a sine wave", "call": "window_isolation_forest(DEMO, 10, 3)", "visible": True},
    {"name": "k = 1", "call": "window_isolation_forest(DEMO, 10, 1)", "visible": True},
    {"name": "window 5, k = 5", "call": "window_isolation_forest(DEMO, 5, 5)"},
    {"name": "tiny series", "call": "window_isolation_forest([1, 2, 3, 4, 100, 5, 6, 7], 3, 2)"},
    {"name": "level jump in a longer series", "call": "window_isolation_forest(BIG, 20, 6)"},
]
