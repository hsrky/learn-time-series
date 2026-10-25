import numpy as np


def holt_winters(y, m, alpha, beta, gamma, h, seasonal="add"):
    y = np.asarray(y, dtype=float)
    n = len(y)
    if n < 2 * m:
        raise ValueError("need at least two full seasons")
    mul = seasonal == "mul"
    # --- start values from the first two seasons ---
    centre = y[:m].mean()                                      # centre of season 1 (time (m-1)/2)
    trend = (y[m:2 * m].mean() - centre) / m                   # average change per step
    line = centre + trend * (np.arange(m) - (m - 1) / 2)       # level line through season 1
    season = (y[:m] / line) if mul else (y[:m] - line)         # one start value per position
    level = line[-1]                                           # level at time m-1
    # --- update for t = m, ..., n-1 ---
    for t in range(m, n):
        i = t % m                                              # position in the season
        s_old = season[i]                                      # s(t-m)
        expected = level + trend
        if mul:
            new_level = alpha * (y[t] / s_old) + (1 - alpha) * expected
            season[i] = gamma * (y[t] / expected) + (1 - gamma) * s_old
        else:
            new_level = alpha * (y[t] - s_old) + (1 - alpha) * expected
            season[i] = gamma * (y[t] - expected) + (1 - gamma) * s_old
        trend = beta * (new_level - level) + (1 - beta) * trend
        level = new_level
    # --- forecast ---
    out = []
    for j in range(1, h + 1):
        base = level + j * trend
        s = season[(n - 1 + j) % m]
        out.append(float(base * s if mul else base + s))
    return {"level": float(level), "trend": float(trend), "season": [float(v) for v in season], "forecast": out}
