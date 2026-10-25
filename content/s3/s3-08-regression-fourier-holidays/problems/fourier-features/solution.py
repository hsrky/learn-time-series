import numpy as np


def fourier_features(t, period, K):
    t = np.asarray(t, dtype=float)
    cols = []
    for k in range(1, K + 1):
        angle = 2 * np.pi * k * t / period       # k waves per period
        cols.append(np.sin(angle))
        cols.append(np.cos(angle))
    if not cols:
        return np.empty((len(t), 0))
    return np.column_stack(cols)


def fourier_names(prefix, K):
    names = []
    for k in range(1, K + 1):
        names += [f"{prefix}_sin{k}", f"{prefix}_cos{k}"]
    return names
