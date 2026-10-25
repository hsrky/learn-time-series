import numpy as np
from numpy.lib.stride_tricks import sliding_window_view


def make_windows(series, input_len, horizon, stride=1):
    """Return (X, y). X: [n, input_len, features], y: [n, horizon] (column 0)."""
    s = np.asarray(series, dtype=float)
    if s.ndim == 1:
        s = s[:, None]                      # [time] -> [time, 1]
    T, F = s.shape
    total = input_len + horizon
    if T < total:                           # no window fits
        return np.empty((0, input_len, F)), np.empty((0, horizon))
    w = sliding_window_view(s, total, axis=0)   # [T-total+1, F, total]  (a view)
    w = w[::stride].transpose(0, 2, 1)          # [n, total, F]
    X = w[:, :input_len, :].copy()              # the past, all features
    y = w[:, input_len:, 0].copy()              # the future, target column only
    return X, y
