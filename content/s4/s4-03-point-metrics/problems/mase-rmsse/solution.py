import numpy as np


def _diffs(y_train, m):
    y_train = np.asarray(y_train, dtype=float)
    if len(y_train) <= m:
        return None
    return y_train[m:] - y_train[:-m]            # lag-m differences


def mase(y_true, y_pred, y_train, m=1):
    """Mean absolute scaled error with a lag-m naive scale from y_train."""
    d = _diffs(y_train, m)
    if d is None:
        return float("nan")
    scale = np.abs(d).mean()
    if scale == 0:
        return float("nan")
    err = np.abs(np.asarray(y_true, dtype=float) - np.asarray(y_pred, dtype=float)).mean()
    return float(err / scale)


def rmsse(y_true, y_pred, y_train, m=1):
    """Root mean squared scaled error with a lag-m naive scale from y_train."""
    d = _diffs(y_train, m)
    if d is None:
        return float("nan")
    scale2 = (d ** 2).mean()
    if scale2 == 0:
        return float("nan")
    mse = ((np.asarray(y_true, dtype=float) - np.asarray(y_pred, dtype=float)) ** 2).mean()
    return float(np.sqrt(mse / scale2))
