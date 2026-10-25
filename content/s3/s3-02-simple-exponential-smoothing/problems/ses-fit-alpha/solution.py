import numpy as np


def _sse_and_level(y, alpha):
    level = y[0]
    sse = 0.0
    for value in y[1:]:
        e = value - level            # one-step error: forecast = old level
        sse += e * e
        level += alpha * e
    return sse, level


def fit_ses_alpha(y, grid):
    y = np.asarray(y, dtype=float)
    best = None
    for alpha in sorted(grid):               # ascending: ties keep the smaller alpha
        sse, level = _sse_and_level(y, alpha)
        if best is None or sse < best[0] - 1e-12:
            best = (sse, alpha, level)
    return {"alpha": float(best[1]), "sse": round(float(best[0]), 4), "forecast": round(float(best[2]), 4)}
