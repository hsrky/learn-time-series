import numpy as np


def make_windows(y, window, horizon=1, stride=1):
    """Return (X, Y): X has `window` columns, Y has `horizon` columns."""
    y = np.asarray(y, dtype=float)
    last_start = len(y) - window - horizon            # last allowed start position
    if last_start < 0:
        return np.empty((0, window)), np.empty((0, horizon))
    starts = np.arange(0, last_start + 1, stride)
    X = y[starts[:, None] + np.arange(window)]        # feature positions
    Y = y[starts[:, None] + window + np.arange(horizon)]   # the next `horizon` values
    return X, Y
