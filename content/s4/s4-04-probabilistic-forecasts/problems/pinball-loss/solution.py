import numpy as np


def pinball_loss(y_true, y_pred, tau):
    """Mean pinball loss of the quantile forecast y_pred at level tau."""
    y = np.asarray(y_true, dtype=float)
    q = np.asarray(y_pred, dtype=float)
    if len(y) == 0:
        return float("nan")
    d = y - q                                         # positive when the forecast is too low
    return float(np.mean(np.where(d >= 0, tau * d, (tau - 1) * d)))


def weighted_quantile_loss(y_true, preds, taus):
    """2 * summed pinball loss / (number of levels * sum |y_true|)."""
    y = np.asarray(y_true, dtype=float)
    total = np.abs(y).sum()
    if total == 0:
        return float("nan")
    s = 0.0
    for q, tau in zip(preds, taus):
        d = y - np.asarray(q, dtype=float)
        s += np.where(d >= 0, tau * d, (tau - 1) * d).sum()   # sum over points
    return float(2 * s / (len(taus) * total))
