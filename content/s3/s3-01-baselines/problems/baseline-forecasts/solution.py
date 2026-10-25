import numpy as np


def baseline_forecast(y, h, method, m=1):
    y = np.asarray(y, dtype=float)
    n = len(y)
    j = np.arange(1, h + 1)                          # steps ahead: 1..h
    if method == "mean":
        return np.full(h, y.mean())
    if method == "naive":
        return np.full(h, y[-1])
    if method == "seasonal_naive":
        if n < m:
            raise ValueError("need at least one full season")
        return y[n - m + (j - 1) % m]                # cycle through the last season
    if method == "drift":
        slope = (y[-1] - y[0]) / (n - 1) if n > 1 else 0.0
        return y[-1] + j * slope
    raise ValueError("unknown method")
