import numpy as np
from statsmodels.tsa.stattools import acf


def dominant_season(y, max_lag):
    """Lag in 2..max_lag with the highest ACF of the first-differenced series (smaller lag on ties)."""
    raise NotImplementedError
