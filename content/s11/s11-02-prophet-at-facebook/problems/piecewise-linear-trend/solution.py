import numpy as np


def _design(t, changepoints):
    cols = [np.ones_like(t), t]
    cols += [np.maximum(0.0, t - c) for c in changepoints]   # hinge: slope change after c
    return np.column_stack(cols)


def piecewise_trend(y, changepoints, horizon=0):
    y = np.asarray(y, dtype=float)
    n = len(y)
    t = np.arange(n, dtype=float)
    coef = np.linalg.lstsq(_design(t, changepoints), y, rcond=None)[0]
    t_all = np.arange(n + horizon, dtype=float)
    return _design(t_all, changepoints) @ coef
