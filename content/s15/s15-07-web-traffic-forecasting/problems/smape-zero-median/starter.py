import numpy as np


def smape(y_true, y_pred):
    """SMAPE in percent (0 to 200). NaN actuals are ignored; 0 vs 0 counts as no error."""
    raise NotImplementedError


def median_forecast(history, horizon, window):
    """Median of the last `window` non-missing values, repeated `horizon` times."""
    raise NotImplementedError
