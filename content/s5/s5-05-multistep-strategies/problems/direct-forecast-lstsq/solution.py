import numpy as np


def direct_forecast(y, p, h):
    """One least-squares model per horizon step; return an array of h forecasts."""
    y = np.asarray(y, dtype=float)
    last = np.r_[y[-p:], 1.0]                         # the same input for every step
    out = np.full(h, np.nan)
    for k in range(1, h + 1):
        n = len(y) - p - k + 1                        # rows available for step k
        if n < 1:
            continue                                  # not enough data -> nan
        X = np.array([y[i:i + p] for i in range(n)])
        A = np.c_[X, np.ones(n)]
        target = y[p + k - 1:p + k - 1 + n]           # value k steps after each window
        w, *_ = np.linalg.lstsq(A, target, rcond=None)
        out[k - 1] = float(last @ w)
    return out
