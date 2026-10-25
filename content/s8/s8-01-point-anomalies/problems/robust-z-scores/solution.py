import numpy as np


def robust_anomalies(values, threshold=3.5):
    x = np.asarray(values, dtype=float)
    m = np.median(x)
    mad = np.median(np.abs(x - m))
    if mad == 0:
        mask = x != m
    else:
        mask = np.abs(0.6745 * (x - m) / mad) > threshold
    return [int(i) for i in np.flatnonzero(mask)]
