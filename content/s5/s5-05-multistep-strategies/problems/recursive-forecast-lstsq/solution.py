import numpy as np


def recursive_forecast(y, p, h):
    """Fit AR(p) with intercept by least squares and forecast h steps recursively."""
    y = np.asarray(y, dtype=float)
    n = len(y) - p                                    # number of training rows
    X = np.array([y[i:i + p] for i in range(n)])      # p consecutive values per row
    A = np.c_[X, np.ones(n)]                          # intercept column
    target = y[p:]
    w, *_ = np.linalg.lstsq(A, target, rcond=None)
    hist = list(y[-p:])
    out = []
    for _ in range(h):
        nxt = float(np.r_[hist[-p:], 1.0] @ w)        # one-step prediction
        out.append(nxt)
        hist.append(nxt)                              # feed the prediction back
    return np.array(out)
