import numpy as np


def ar_forecast(y, coefs, h):
    coefs = np.asarray(coefs, dtype=float)
    p = len(coefs) - 1
    if len(y) < p:
        raise ValueError("history is shorter than the model order")
    hist = [float(v) for v in y]                 # work on a copy
    out = []
    for _ in range(h):
        lags = hist[-1:-p - 1:-1]                # y[t-1], y[t-2], ..., y[t-p]
        nxt = coefs[0] + float(np.dot(coefs[1:], lags))
        out.append(nxt)
        hist.append(nxt)                         # feed the forecast back in
    return np.array(out)
