import numpy as np


def _scale(win):
    s = np.mean(np.abs(win))
    return s if s != 0 else 1.0


def global_ar_forecast(series, p):
    """One pooled, window-scaled AR(p) model; one-step forecast for every series."""
    rows, targets = [], []
    for y in series.values():
        y = np.asarray(y, dtype=float)
        for i in range(len(y) - p):
            win = y[i:i + p]
            s = _scale(win)
            rows.append(np.r_[win / s, 1.0])           # scaled lags + intercept
            targets.append(y[i + p] / s)
    out = {}
    if not rows:
        return {k: float("nan") for k in series}
    w, *_ = np.linalg.lstsq(np.array(rows), np.array(targets), rcond=None)
    for k, y in series.items():
        y = np.asarray(y, dtype=float)
        if len(y) < p:
            out[k] = float("nan")
            continue
        win = y[-p:]
        s = _scale(win)
        out[k] = float(np.r_[win / s, 1.0] @ w * s)    # back to the original scale
    return out
