import math
import numpy as np


def split_conformal(cal_residuals, y_pred, alpha):
    """Return (lower, upper) arrays of split conformal intervals."""
    r = np.sort(np.asarray(cal_residuals, dtype=float))
    p = np.asarray(y_pred, dtype=float)
    n = len(r)
    if n == 0:
        nan = np.full(len(p), np.nan)
        return nan, nan.copy()
    k = math.ceil(round((n + 1) * (1 - alpha), 9))     # rank of the quantile
    q = r[k - 1] if k <= n else np.inf                 # too few points -> infinite interval
    return p - q, p + q
