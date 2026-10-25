import math
import numpy as np


def rolling_conformal(y, yhat, alpha, window):
    """Return (lower, upper) rolling conformal intervals using only past residuals."""
    y = np.asarray(y, dtype=float)
    yhat = np.asarray(yhat, dtype=float)
    n = len(y)
    res = np.abs(y - yhat)
    lower = np.full(n, np.nan)
    upper = np.full(n, np.nan)
    for t in range(n):
        r = res[max(0, t - window):t]          # residuals known at time t (not t itself)
        r = r[~np.isnan(r)]                    # skip missing residuals
        m = len(r)
        if m == 0:
            continue
        k = math.ceil(round((m + 1) * (1 - alpha), 9))
        q = np.sort(r)[k - 1] if k <= m else np.inf
        lower[t] = yhat[t] - q
        upper[t] = yhat[t] + q
    return lower, upper
