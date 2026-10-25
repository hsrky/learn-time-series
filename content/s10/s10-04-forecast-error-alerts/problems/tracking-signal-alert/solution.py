import numpy as np


def tracking_signal(actual, forecast):
    err = np.asarray(actual, dtype=float) - np.asarray(forecast, dtype=float)
    n = len(err)
    rsfe = np.cumsum(err)                                   # running sum keeps the sign
    mad = np.cumsum(np.abs(err)) / np.arange(1, n + 1)      # running mean absolute error
    ts = np.zeros(n)
    np.divide(rsfe, mad, out=ts, where=mad > 0)             # 0 where MAD is 0
    return ts


def first_alarm(actual, forecast, limit=4.0, min_periods=6):
    ts = tracking_signal(actual, forecast)
    count = np.arange(1, len(ts) + 1)
    hit = np.flatnonzero((np.abs(ts) > limit) & (count >= min_periods))
    return int(hit[0]) if len(hit) else -1
