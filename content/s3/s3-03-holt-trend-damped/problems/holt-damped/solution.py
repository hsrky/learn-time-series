import numpy as np


def holt(y, alpha, beta, h, phi=1.0):
    y = np.asarray(y, dtype=float)
    level, trend = y[0], y[1] - y[0]               # start values
    for value in y[1:]:
        new_level = alpha * value + (1 - alpha) * (level + phi * trend)
        trend = beta * (new_level - level) + (1 - beta) * phi * trend
        level = new_level
    damp = np.cumsum(phi ** np.arange(1, h + 1))   # phi + phi^2 + ... + phi^j
    forecast = level + damp * trend
    return {"level": float(level), "trend": float(trend), "forecast": [float(v) for v in forecast]}
