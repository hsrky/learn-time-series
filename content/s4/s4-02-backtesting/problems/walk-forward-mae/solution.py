import numpy as np


def walk_forward_mae(y, forecaster, initial, horizon, step=1):
    """Mean absolute error at each horizon step, averaged over expanding-window folds."""
    y = np.asarray(y, dtype=float)
    errors = []
    end = initial
    while end + horizon <= len(y):                    # complete folds only
        pred = np.asarray(forecaster(y[:end], horizon), dtype=float)   # past only
        errors.append(np.abs(y[end:end + horizon] - pred))
        end += step
    if not errors:
        return np.full(horizon, np.nan)
    return np.mean(errors, axis=0)                    # one number per horizon step
