import numpy as np


def _smape_mase(x, y, f, m):
    x, y, f = (np.asarray(a, dtype=float) for a in (x, y, f))
    smape = np.mean(200.0 * np.abs(y - f) / (np.abs(y) + np.abs(f)))
    scale = np.mean(np.abs(x[m:] - x[:-m]))          # in-sample seasonal naive error
    mase = np.mean(np.abs(y - f)) / scale
    return smape, mase


def owa(train, test, fc, fc_naive2, m):
    mine = np.array([_smape_mase(x, y, f, m) for x, y, f in zip(train, test, fc)])
    base = np.array([_smape_mase(x, y, f, m) for x, y, f in zip(train, test, fc_naive2)])
    smape, mase = mine.mean(axis=0)                   # average over series
    smape_b, mase_b = base.mean(axis=0)
    return float(0.5 * (smape / smape_b + mase / mase_b))
