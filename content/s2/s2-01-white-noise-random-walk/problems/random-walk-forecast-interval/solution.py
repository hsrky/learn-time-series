import numpy as np


def random_walk_forecast(last, h, sigma, drift=0.0, z=1.96):
    k = np.arange(1, h + 1)                  # steps ahead: 1..h
    forecast = last + drift * k              # last value plus drift for k steps
    half = z * sigma * np.sqrt(k)            # error sd grows like sqrt(k)
    return {
        "forecast": forecast.tolist(),
        "lower": (forecast - half).tolist(),
        "upper": (forecast + half).tolist(),
    }
