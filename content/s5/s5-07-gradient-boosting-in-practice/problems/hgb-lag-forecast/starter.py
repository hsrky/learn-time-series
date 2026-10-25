import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor


def forecast(y_train, horizon):
    """Return `horizon` forecasts for the days after y_train."""
    # Your code here: lag features -> HistGradientBoostingRegressor -> recursive forecast
    raise NotImplementedError
