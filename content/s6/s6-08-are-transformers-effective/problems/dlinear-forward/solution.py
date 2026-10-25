import numpy as np
from numpy.lib.stride_tricks import sliding_window_view


def dlinear_forward(x, W_trend, W_rem, kernel):
    """x: [batch, L]; W_*: [L, H]; returns [batch, H]."""
    x = np.asarray(x, dtype=float)
    pad = (kernel - 1) // 2
    # repeat first / last value so the moving average keeps the same length
    padded = np.concatenate([np.repeat(x[:, :1], pad, axis=1), x,
                             np.repeat(x[:, -1:], pad, axis=1)], axis=1)
    trend = sliding_window_view(padded, kernel, axis=1).mean(axis=-1)   # [batch, L]
    remainder = x - trend
    return trend @ W_trend + remainder @ W_rem
