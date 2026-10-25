import numpy as np


def ses(y, alpha, h):
    y = np.asarray(y, dtype=float)
    level = y[0]                           # start level = first observation
    levels = [level]
    for value in y[1:]:
        level = alpha * value + (1 - alpha) * level
        levels.append(level)
    return {"level": [float(v) for v in levels], "forecast": [float(level)] * h}
