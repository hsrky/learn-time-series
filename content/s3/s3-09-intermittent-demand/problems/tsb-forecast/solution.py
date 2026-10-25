import numpy as np


def tsb_path(y, alpha, beta):
    y = np.asarray(y, dtype=float)
    demand = np.nonzero(y > 0)[0]
    out = [0.0] * len(y)
    if len(demand) == 0:
        return out
    first = int(demand[0])
    z, prob = y[first], 1.0 / (first + 1)
    out[first] = float(prob * z)
    for t in range(first + 1, len(y)):
        if y[t] > 0:
            z = alpha * y[t] + (1 - alpha) * z           # size: only when there is a sale
            prob = beta + (1 - beta) * prob              # probability goes up
        else:
            prob = (1 - beta) * prob                     # probability decays in a zero
        out[t] = float(prob * z)
    return out


def tsb(y, alpha, beta):
    path = tsb_path(y, alpha, beta)
    return path[-1] if path else 0.0
