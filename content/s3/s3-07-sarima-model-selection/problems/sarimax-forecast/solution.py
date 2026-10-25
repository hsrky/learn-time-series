import warnings

import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX


def best_sarimax(y, candidates, h):
    y = np.asarray(y, dtype=float)
    best = None
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for i, (order, seasonal_order) in enumerate(candidates):
            fit = SARIMAX(y, order=order, seasonal_order=seasonal_order).fit(disp=False)
            if best is None or fit.aic < best[0] - 1e-9:      # strict: ties keep the lowest index
                best = (fit.aic, i, np.asarray(fit.forecast(h)))
    return {"best": int(best[1]), "aic": round(float(best[0]), 1),
            "forecast": [round(float(v), 2) for v in best[2]]}


def seasonal_naive(y, m, h):
    y = [float(v) for v in y]
    last = y[-m:]
    return [last[i % m] for i in range(h)]
