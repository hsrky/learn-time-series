import numpy as np


def integrate_forecast(history, diff_forecast, d):
    history = np.asarray(history, dtype=float)
    x = np.asarray(diff_forecast, dtype=float)
    if len(history) < d:
        raise ValueError("not enough history for d differences")
    if d == 0:
        return x
    # last value of each differenced history: L[j] = last value of diff^j(history)
    last = [np.diff(history, n=j)[-1] if j > 0 else history[-1] for j in range(d)]
    for j in range(d - 1, -1, -1):          # undo the d-th difference first
        x = last[j] + np.cumsum(x)
    return x
