import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import TimeSeriesSplit


def backtest_mae(y, n_lags, n_splits, gap):
    """Mean over TimeSeriesSplit folds of the MAE of a LinearRegression on lag features.

    Row for time t: X[t] = [y[t-1], ..., y[t-n_lags]], target y[t], for t = n_lags .. len(y)-1.
    """
    raise NotImplementedError
