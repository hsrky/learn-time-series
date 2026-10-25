import numpy as np


def smape(y_true, y_pred):
    """SMAPE in percent (0 to 200). NaN actuals are ignored; 0 vs 0 counts as no error."""
    y = np.asarray(y_true, dtype=float)
    p = np.asarray(y_pred, dtype=float)
    valid = ~np.isnan(y)                              # missing actuals are not scored
    y, p = y[valid], p[valid]
    if len(y) == 0:
        return 0.0
    num = np.abs(p - y)
    den = np.abs(y) + np.abs(p)
    err = np.where(den == 0, 0.0, 200.0 * num / np.where(den == 0, 1.0, den))   # 0 vs 0 -> 0
    return float(err.mean())


def median_forecast(history, horizon, window):
    """Median of the last `window` non-missing values, repeated `horizon` times."""
    h = np.asarray(history, dtype=float)[-window:] if window > 0 else np.array([])
    h = h[~np.isnan(h)]
    level = float(np.median(h)) if len(h) else 0.0
    return np.full(horizon, level)
