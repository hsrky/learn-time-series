import numpy as np


def croston(y, alpha, variant="croston"):
    if variant not in ("croston", "sba"):
        raise ValueError("variant must be 'croston' or 'sba'")
    y = np.asarray(y, dtype=float)
    demand = np.nonzero(y > 0)[0]
    if len(demand) == 0:
        return 0.0
    first = int(demand[0])
    z, p, last = y[first], first + 1.0, first            # start values from the first demand
    for t in range(first + 1, len(y)):
        if y[t] > 0:                                     # update only when there is a demand
            q = t - last                                 # periods since the last demand
            z = alpha * y[t] + (1 - alpha) * z
            p = alpha * q + (1 - alpha) * p
            last = t
    forecast = z / p
    if variant == "sba":
        forecast *= (1 - alpha / 2)                      # bias correction
    return float(forecast)
