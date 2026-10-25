import numpy as np


def ols_reconcile(S, y_hat):
    S = np.asarray(S, dtype=float)
    y = np.asarray(y_hat, dtype=float)
    b = np.linalg.solve(S.T @ S, S.T @ y)            # normal equations: (S'S) b = S'y
    return {"bottom": [float(v) for v in b], "all": [float(v) for v in S @ b]}


def is_coherent(S, y, tol=1e-9):
    S = np.asarray(S, dtype=float)
    y = np.asarray(y, dtype=float)
    m = S.shape[1]
    return bool(np.allclose(y, S @ y[-m:], atol=tol, rtol=0))
