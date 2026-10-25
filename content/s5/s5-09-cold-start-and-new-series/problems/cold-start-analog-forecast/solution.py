import numpy as np


def cold_start_forecast(new_hist, analogs, horizon, k=2):
    """Forecast the next `horizon` values of a new series from similar older series."""
    h = np.asarray(new_hist, dtype=float)
    L = len(h)
    if L == 0:
        ok = [np.asarray(a, dtype=float)[:horizon] for a in analogs if len(a) >= horizon]
        return np.mean(ok, axis=0) if ok else np.full(horizon, np.nan)
    level = h.mean()
    if level == 0:
        return np.zeros(horizon)
    valid = []
    for a in analogs:
        a = np.asarray(a, dtype=float)
        if len(a) >= L + horizon and a[:L].mean() > 0:      # long enough and positive level
            valid.append(a)
    if not valid:
        return np.full(horizon, level)
    shape = h / level
    d = np.array([np.abs(shape - a[:L] / a[:L].mean()).mean() for a in valid])
    best = np.argsort(d, kind="stable")[:k]                 # ties keep the lower position
    futures = [valid[i][L:L + horizon] / valid[i][:L].mean() for i in best]
    return np.mean(futures, axis=0) * level                 # shape x level of the new series
