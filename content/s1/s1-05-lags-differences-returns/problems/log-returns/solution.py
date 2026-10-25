import numpy as np
import pandas as pd


def log_returns(prices):
    """Return ln(p[t] / p[t-1]) for each t; the first value is NaN."""
    return np.log(prices / prices.shift(1))      # ratio with the previous price, then ln
