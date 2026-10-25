import numpy as np


def fit_ar(y, p):
    y = np.asarray(y, dtype=float)
    n = len(y)
    target = y[p:]                                         # y[t] for t = p..n-1
    cols = [np.ones(n - p)]                                # constant
    cols += [y[p - k:n - k] for k in range(1, p + 1)]      # lag k column: y[t-k]
    X = np.column_stack(cols)
    beta, *_ = np.linalg.lstsq(X, target, rcond=None)
    return beta
