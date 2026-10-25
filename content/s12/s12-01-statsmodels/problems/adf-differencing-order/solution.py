import numpy as np
from statsmodels.tsa.stattools import adfuller


def differencing_order(y, alpha=0.05, max_d=2):
    x = np.asarray(y, dtype=float)
    d = 0
    while True:
        if len(x) < 10 or np.ptp(x) == 0:           # cannot test: stop here
            return d
        p_value = adfuller(x, autolag="AIC")[1]      # H0: unit root (non-stationary)
        if p_value < alpha:
            return d
        if d == max_d:
            return max_d
        x = np.diff(x)                               # difference once more
        d += 1
