import numpy as np


def linear_trend(y):
    """Return (slope, intercept) of the least-squares line through the non-nan points."""
    y = np.asarray(y, dtype=float)
    t = np.arange(len(y), dtype=float)       # position of every value, also the missing ones
    ok = ~np.isnan(y)                        # keep the valid points
    t, y = t[ok], y[ok]
    t_mean, y_mean = t.mean(), y.mean()
    slope = ((t - t_mean) * (y - y_mean)).sum() / ((t - t_mean) ** 2).sum()
    intercept = y_mean - slope * t_mean
    return float(slope), float(intercept)
