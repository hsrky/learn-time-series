import numpy as np
from statsmodels.tsa.stattools import adfuller


def differencing_order(y, alpha=0.05, max_d=2):
    """Smallest d (up to max_d) after which the ADF p-value is below alpha.

    Return d early if the current series has < 10 values or is constant.
    """
    raise NotImplementedError
