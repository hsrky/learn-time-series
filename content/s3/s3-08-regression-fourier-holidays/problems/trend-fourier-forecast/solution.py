import numpy as np


def trend_fourier_forecast(y, period, K, h):
    y = np.asarray(y, dtype=float)
    n = len(y)

    def features(t):
        t = np.asarray(t, dtype=float)
        cols = [np.ones(len(t)), t]                       # constant and linear trend
        for k in range(1, K + 1):
            angle = 2 * np.pi * k * t / period
            cols += [np.sin(angle), np.cos(angle)]
        return np.column_stack(cols)

    beta, *_ = np.linalg.lstsq(features(np.arange(n)), y, rcond=None)
    return features(np.arange(n, n + h)) @ beta           # future times continue the index
