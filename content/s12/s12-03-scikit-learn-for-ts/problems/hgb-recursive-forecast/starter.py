import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor


def hgb_forecast(y, h, n_lags):
    """Recursive h-step forecast with HistGradientBoostingRegressor(max_iter=200, random_state=0).

    Features of row t: [y[t-1], ..., y[t-n_lags]]. Return a numpy array of length h.
    """
    raise NotImplementedError
