import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor


def hgb_forecast(y, h, n_lags):
    y = np.asarray(y, dtype=float)
    X = np.column_stack([y[n_lags - j: len(y) - j] for j in range(1, n_lags + 1)])
    target = y[n_lags:]
    model = HistGradientBoostingRegressor(max_iter=200, random_state=0).fit(X, target)
    hist = list(y)
    out = []
    for _ in range(h):
        x = np.array(hist[-1: -n_lags - 1: -1]).reshape(1, -1)   # [newest, ..., oldest]
        p = float(model.predict(x)[0])
        out.append(p)
        hist.append(p)                                            # feed the forecast back
    return np.array(out)
