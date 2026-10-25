import numpy as np

X3 = np.array([2.0, 4.0, 6.0])
rng = np.random.default_rng(21)
XB = np.abs(rng.normal(loc=500, scale=120, size=200))
XN = np.array([1.0, np.nan, 3.0, 2.0])

def check(got, exp, case):
    # compare tuples / arrays, NaN-aware
    if isinstance(exp, tuple):
        if not (isinstance(got, tuple) and len(got) == 2):
            return False, "expected a tuple (tokens, scale)"
        t, s = got
        if not np.array_equal(np.asarray(t), exp[0]):
            return False, f"tokens differ: {np.asarray(t)[:8]} vs {exp[0][:8]}"
        if abs(float(s) - exp[1]) > 1e-9:
            return False, f"scale {s} != {exp[1]}"
        return True, ""
    g = np.atleast_1d(np.asarray(got, dtype=float)); exp = np.atleast_1d(np.asarray(exp, dtype=float))
    if g.shape != exp.shape:
        return False, f"shape {g.shape} != {exp.shape}"
    return bool(np.allclose(g, exp, equal_nan=True, atol=1e-9)), "values differ"

CASES = [
    {"name": "tokenize 2,4,6", "call": "tokenize(X3)", "visible": True},
    {"name": "detokenize", "call": "detokenize(np.array([11, 12, 13]), 4.0)", "visible": True},
    {"name": "NaN becomes PAD", "call": "tokenize(XN)", "visible": True},
    {"name": "detokenize PAD is NaN", "call": "detokenize(np.array([0, 5, 9]), 2.0)"},
    {"name": "all zeros: scale 1", "call": "tokenize(np.zeros(4))"},
    {"name": "all NaN", "call": "tokenize(np.array([np.nan, np.nan]))"},
    {"name": "outliers are clipped", "call": "tokenize(np.array([1.0, 1.0, 1.0, 100.0]))"},
    {"name": "negative values", "call": "tokenize(np.array([-3.0, 0.0, 3.0]), n_bins=8, low=-2.0, high=2.0)"},
    {"name": "random 200, 64 bins", "call": "tokenize(XB, n_bins=64)"},
    {"name": "round trip error is small", "call": "(lambda r: float(np.abs(detokenize(r[0], r[1], 64) - XB).max() <= 0.5 * (8 / 64) * r[1] + 1e-9))(tokenize(XB, 64))", "expected": "1.0"},
]
