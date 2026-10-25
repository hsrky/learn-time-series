import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing


def ets_forecast(train, h, m):
    model = ExponentialSmoothing(np.asarray(train, dtype=float), trend="add",
                                 seasonal="add", seasonal_periods=m)
    fit = model.fit()                      # estimates alpha, beta, gamma by maximum likelihood
    return np.asarray(fit.forecast(h))     # plain array of length h
