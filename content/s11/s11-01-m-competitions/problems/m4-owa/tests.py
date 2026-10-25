import numpy as np

TR1, TE1, FC1, N1 = [np.array([10, 12, 14, 16.0])], [np.array([18, 20.0])], [np.array([17, 22.0])], [np.array([16, 16.0])]

rng = np.random.default_rng(4)
def make(k, m):
    tr, te, fc, nv = [], [], [], []
    for _ in range(k):
        n = int(rng.integers(3 * m + 2, 60))
        level = rng.uniform(50, 500)
        t = np.arange(n + 6)
        s = level * (1 + 0.2 * np.sin(2 * np.pi * t / m) + 0.01 * t) if m > 1 else level + 2 * t
        y = s * (1 + rng.normal(0, 0.03, len(t)))
        tr.append(y[:n]); te.append(y[n:])
        fc.append(y[n:] * (1 + rng.normal(0, 0.05, 6)))
        nv.append(np.repeat(y[n - 1], 6))
    return tr, te, fc, nv
BT, BE, BF, BN = make(300, 12)
ST, SE, SF, SN = make(50, 1)

CASES = [
    {"name": "single series from the statement", "call": "owa(TR1, TE1, FC1, N1, 1)", "visible": True, "expected": "0.4742", "tol": 1e-3},
    {"name": "method equals Naive2 gives 1", "call": "owa(TR1, TE1, N1, N1, 1)", "visible": True, "expected": "1.0"},
    {"name": "seasonal lag m=2", "call": "owa([np.array([10, 21, 11, 19, 12, 20.0])], [np.array([10, 20.0])], [np.array([11, 19.0])], [np.array([20, 20.0])], 2)", "visible": True},
    {"name": "two series with different length", "call": "owa([np.array([1, 2, 3.0]), np.array([5, 5, 6, 7, 9.0])], [np.array([4.0]), np.array([10.0])], [np.array([3.5]), np.array([9.0])], [np.array([3.0]), np.array([9.0])], 1)"},
    {"name": "perfect forecast gives 0", "call": "owa(TR1, TE1, TE1, N1, 1)", "expected": "0.0"},
    {"name": "random monthly set", "call": "owa(BT, BE, BF, BN, 12)"},
    {"name": "random non-seasonal set", "call": "owa(ST, SE, SF, SN, 1)"},
]
