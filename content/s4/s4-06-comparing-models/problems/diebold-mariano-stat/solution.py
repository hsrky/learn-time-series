import math
import numpy as np


def dm_test(e1, e2, h=1, power=2):
    """Return {"stat": ..., "p_value": ...} for the Diebold-Mariano test."""
    e1 = np.asarray(e1, dtype=float)
    e2 = np.asarray(e2, dtype=float)
    n = len(e1)
    nan = {"stat": float("nan"), "p_value": float("nan")}
    if n < 2:
        return nan
    d = np.abs(e1) ** power - np.abs(e2) ** power     # loss difference
    dbar = d.mean()
    dc = d - dbar
    v = np.sum(dc * dc) / n                           # g0
    for k in range(1, h):                             # autocovariances up to lag h-1
        v += 2 * np.sum(dc[k:] * dc[:n - k]) / n
    if v <= 0:
        return nan
    stat = dbar / math.sqrt(v / n)
    p = math.erfc(abs(stat) / math.sqrt(2))           # two-sided normal p-value
    return {"stat": float(stat), "p_value": float(p)}
