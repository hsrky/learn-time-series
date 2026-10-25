import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing


def ets_forecast(train, h, m):
    """Additive Holt-Winters (trend='add', seasonal='add') forecast of h steps."""
    raise NotImplementedError
