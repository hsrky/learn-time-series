import numpy as np
from scipy import stats


def generalized_esd(values, r, alpha=0.05):
    x = np.asarray(values, dtype=float)
    idx = list(range(len(x)))              # original positions still in the sample
    removed, R, lam = [], [], []
    for i in range(1, r + 1):
        m = len(idx)
        if m < 3:
            break
        cur = x[idx]
        s = cur.std(ddof=1)
        if s == 0:
            break
        dev = np.abs(cur - cur.mean())
        j = int(np.argmax(dev))            # most extreme point
        R.append(dev[j] / s)
        removed.append(idx.pop(j))
        p = 1 - alpha / (2 * m)
        t = stats.t.ppf(p, m - 2)
        lam.append((m - 1) * t / np.sqrt((m - 2 + t ** 2) * m))
    k = 0
    for i in range(len(R)):
        if R[i] > lam[i]:
            k = i + 1                       # largest i that passes
    return sorted(int(p) for p in removed[:k])
