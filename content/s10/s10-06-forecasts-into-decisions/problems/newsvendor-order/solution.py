import math
import numpy as np


def expected_cost(q, samples, cu, co):
    d = np.asarray(samples, dtype=float)
    short = np.maximum(d - q, 0.0)       # units we could not sell
    left = np.maximum(q - d, 0.0)        # units left over
    return float(np.mean(cu * short + co * left))


def newsvendor_order(samples, cu, co):
    d = np.sort(np.asarray(samples, dtype=float))
    n = len(d)
    r = cu / (cu + co)                                   # critical ratio
    k = max(1, math.ceil(r * n - 1e-9))                  # 1-based rank
    return float(d[k - 1])
