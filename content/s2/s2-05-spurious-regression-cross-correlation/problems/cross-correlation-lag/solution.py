import numpy as np


def best_lead_lag(x, y, max_lag, difference=True):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if difference:
        x, y = np.diff(x), np.diff(y)          # remove trends first
    n = len(x)
    best = None
    for k in range(-max_lag, max_lag + 1):
        if k >= 0:
            a, b = x[:n - k], y[k:]            # x(t) with y(t+k)
        else:
            a, b = x[-k:], y[:n + k]           # y leads: x(t-k) with y(t)
        if len(a) < 3 or np.std(a) == 0 or np.std(b) == 0:
            continue                           # not enough data / constant slice
        r = float(np.corrcoef(a, b)[0, 1])
        key = (-round(abs(r), 12), abs(k), -k)  # best |r|, then small |k|, then positive
        if best is None or key < best[0]:
            best = (key, k, r)
    if best is None:
        return {"lag": 0, "corr": 0.0}
    return {"lag": int(best[1]), "corr": round(best[2], 4)}
