import numpy as np
from scipy import stats


def generalized_esd(x, max_outliers, alpha=0.05):
    x = np.asarray(x, dtype=float)
    n = len(x)
    remaining = list(range(n))
    removed, R, lam = [], [], []
    for i in range(1, max_outliers + 1):
        if len(remaining) < 3:
            break
        vals = x[remaining]
        s = vals.std(ddof=1)
        if s == 0:
            break
        j = int(np.argmax(np.abs(vals - vals.mean())))
        R.append(abs(vals[j] - vals.mean()) / s)          # test statistic R_i
        removed.append(remaining.pop(j))                  # remember the ORIGINAL index
        p = alpha / (2 * (n - i + 1))
        t = stats.t.ppf(1 - p, n - i - 1)
        lam.append((n - i) * t / np.sqrt((n - i - 1 + t ** 2) * (n - i + 1)))   # critical value
    k = 0
    for i in range(len(R)):
        if R[i] > lam[i]:
            k = i + 1                                      # largest i that passes
    return sorted(removed[:k])
