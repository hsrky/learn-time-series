import numpy as np

S2 = [[1, 1], [1, 0], [0, 1]]
S3 = [[1, 1, 1, 1], [1, 1, 0, 0], [0, 0, 1, 1], [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
YH3 = [100.0, 58.0, 38.0, 30.0, 26.0, 22.0, 18.0]
_r = np.random.default_rng(2)
S_BIG = np.vstack([np.ones((1, 10)), np.eye(10)])
YH_BIG = _r.uniform(5, 20, 11)

CASES = [
    {"name": "two bottom series", "call": "ols_reconcile(S2, [52, 31, 19])", "visible": True},
    {"name": "already coherent", "call": "ols_reconcile(S2, [50, 30, 20])", "visible": True},
    {"name": "three levels", "call": "ols_reconcile(S3, YH3)"},
    {"name": "result is coherent", "call": "is_coherent(S3, ols_reconcile(S3, YH3)['all'])", "expected": "True"},
    {"name": "input is not coherent", "call": "is_coherent(S3, YH3)", "expected": "False"},
    {"name": "ten bottom series", "call": "ols_reconcile(S_BIG, YH_BIG)", "tol": 1e-8},
    {"name": "sum of bottom equals new total", "call": "abs(sum(ols_reconcile(S_BIG, YH_BIG)['bottom']) - ols_reconcile(S_BIG, YH_BIG)['all'][0]) < 1e-9", "expected": "True"},
    {"name": "single bottom series", "call": "ols_reconcile([[1], [1]], [4.0, 6.0])"},
]
