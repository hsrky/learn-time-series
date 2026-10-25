import numpy as np
from statsmodels.tsa.stattools import acf


def dominant_season(y, max_lag):
    d = np.diff(np.asarray(y, dtype=float))        # remove the trend
    r = acf(d, nlags=max_lag, fft=True)            # r[k] = autocorrelation at lag k
    return int(np.argmax(r[2:]) + 2)               # skip lags 0 and 1
