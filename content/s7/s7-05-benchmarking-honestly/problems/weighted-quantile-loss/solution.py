import numpy as np


def wql(y, quantile_forecasts, levels):
    """Mean over levels of 2 * sum(pinball) / sum(|y|)."""
    y = np.asarray(y, dtype=float)
    f = np.asarray(quantile_forecasts, dtype=float)
    q = np.asarray(levels, dtype=float)[:, None]        # [levels, 1]
    denom = np.abs(y).sum()
    if denom == 0:
        return float("nan")
    e = y[None, :] - f                                   # [levels, time]
    pinball = np.maximum(q * e, (q - 1) * e)             # penalty depends on the sign of the error
    return float(np.mean(2 * pinball.sum(axis=1) / denom))
