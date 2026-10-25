import numpy as np


def acf(x, nlags):
    x = np.asarray(x, dtype=float)
    n = len(x)
    d = x - x.mean()                    # centre the data
    denom = np.sum(d * d)               # lag-0 sum of squares
    out = np.zeros(nlags + 1)
    if denom == 0:                      # constant series
        out[0] = 1.0
        return out
    for k in range(nlags + 1):
        out[k] = np.sum(d[k:] * d[:n - k]) / denom
    return out
