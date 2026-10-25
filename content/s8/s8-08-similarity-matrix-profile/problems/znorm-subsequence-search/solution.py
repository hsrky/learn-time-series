import numpy as np


def znorm_rows(W):
    mu = W.mean(axis=1, keepdims=True)
    sd = W.std(axis=1, keepdims=True)
    flat = sd < 1e-9
    safe = np.where(flat, 1.0, sd)
    Z = (W - mu) / safe
    return np.where(flat, 0.0, Z)


def best_match(series, query):
    x = np.asarray(series, dtype=float)
    q = np.asarray(query, dtype=float)
    m = len(q)
    W = np.lib.stride_tricks.sliding_window_view(x, m)
    Zw = znorm_rows(W)
    Zq = znorm_rows(q[None, :])[0]
    d = np.sqrt(((Zw - Zq) ** 2).sum(axis=1))
    best = d.min()
    start = int(np.flatnonzero(d <= best + 1e-9)[0])     # first window within the tie tolerance
    return (start, round(float(d[start]), 10))
