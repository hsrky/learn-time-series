import numpy as np


def tracking_signal(actual, forecast):
    """ts[t] = running sum of (actual - forecast) / running mean of |actual - forecast|.
    ts is 0 where the running MAD is 0. Return a numpy array."""
    raise NotImplementedError


def first_alarm(actual, forecast, limit=4.0, min_periods=6):
    """0-based index of the first t with |ts| > limit and (t + 1) >= min_periods; -1 if none."""
    raise NotImplementedError
