import numpy as np
import pandas as pd


def rmsle(y_true, y_pred):
    """Root mean squared logarithmic error; negative predictions are clipped to 0."""
    raise NotImplementedError


def seasonal_naive_forecast(train, test_dates, season=7):
    """Forecast each (store_nbr, family) series with the value from the last `season` days.
    Return columns store_nbr, family, date, sales."""
    raise NotImplementedError
