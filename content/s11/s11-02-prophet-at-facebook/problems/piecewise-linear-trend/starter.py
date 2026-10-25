import numpy as np


def piecewise_trend(y, changepoints, horizon=0):
    """Fit y with a + b*t + sum_j d_j*max(0, t - c_j) by least squares.

    Return the fitted trend for t = 0 .. len(y)-1+horizon (extra points continue the last line).
    """
    raise NotImplementedError
