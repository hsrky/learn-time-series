import numpy as np


def lttb(x, y, threshold):
    n = len(x)
    if threshold >= n:
        return list(range(n))
    if threshold == 2:
        return [0, n - 1]
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    every = (n - 2) / (threshold - 2)
    chosen = [0]
    a = 0
    for i in range(threshold - 2):
        s = int((i + 1) * every) + 1
        e = min(int((i + 2) * every) + 1, n)
        cx, cy = x[s:e].mean(), y[s:e].mean()          # average point of the next bucket
        lo, hi = int(i * every) + 1, int((i + 1) * every) + 1
        best, best_area = lo, -1.0
        for j in range(lo, hi):
            area = abs((x[a] - cx) * (y[j] - y[a]) - (x[a] - x[j]) * (cy - y[a])) / 2
            if area > best_area:
                best, best_area = j, area
        chosen.append(best)
        a = best
    chosen.append(n - 1)
    return chosen
