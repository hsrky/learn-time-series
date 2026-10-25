import numpy as np


def ewma(x, alpha):
    """Return the exponentially weighted moving average of x as a numpy array."""
    x = np.asarray(x, dtype=float)
    out = np.full(len(x), np.nan)
    s = np.nan                                   # last smoothed value
    for t, v in enumerate(x):
        if not np.isnan(v):
            if np.isnan(s):
                s = v                            # first real value starts the average
            else:
                s = alpha * v + (1 - alpha) * s  # blend new value and old average
        out[t] = s                               # a nan input keeps the old average
    return out
