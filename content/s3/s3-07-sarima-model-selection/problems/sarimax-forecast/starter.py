import warnings

import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX


def best_sarimax(y, candidates, h):
    """Return {"best": int, "aic": float, "forecast": [h floats]}."""
    raise NotImplementedError


def seasonal_naive(y, m, h):
    """Repeat the last m values to make h forecasts (list of floats)."""
    raise NotImplementedError
