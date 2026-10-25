import numpy as np


def interval_metrics(y, lower, upper, alpha):
    """Return coverage, mean_width, interval_score and calibration_gap."""
    y = np.asarray(y, dtype=float)
    if len(y) == 0:
        nan = float("nan")
        return {"coverage": nan, "mean_width": nan, "interval_score": nan, "calibration_gap": nan}
    a = np.asarray(lower, dtype=float)
    b = np.asarray(upper, dtype=float)
    lo, hi = np.minimum(a, b), np.maximum(a, b)       # fix reversed intervals
    coverage = np.mean((y >= lo) & (y <= hi))
    width = hi - lo
    penalty = (2 / alpha) * (np.maximum(lo - y, 0) + np.maximum(y - hi, 0))
    return {"coverage": float(coverage),
            "mean_width": float(width.mean()),
            "interval_score": float((width + penalty).mean()),
            "calibration_gap": float(coverage - (1 - alpha))}
