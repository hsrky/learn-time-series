import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor

M = 7  # weekly season


def _features(h, i):
    """Features for position i, using only h[:i]. Levels are made relative to lag_7."""
    base = h[i - 7]
    return [h[i - 1] - base, h[i - 2] - base, h[i - 14] - base,
            np.mean(h[i - 7:i]) - base, i % M]


def forecast(y_train, horizon):
    """Train HistGradientBoostingRegressor on lag features and forecast `horizon` steps."""
    y = np.asarray(y_train, dtype=float)
    X = np.array([_features(y, i) for i in range(14, len(y))])
    target = np.array([y[i] - y[i - 7] for i in range(14, len(y))])   # predict the CHANGE from lag 7
    model = HistGradientBoostingRegressor(max_iter=60, learning_rate=0.1,
                                          early_stopping=False, random_state=0)
    model.fit(X, target)
    hist = list(y)
    out = []
    for _ in range(horizon):                       # recursive forecast
        i = len(hist)
        delta = model.predict(np.array([_features(hist, i)]))[0]
        nxt = hist[i - 7] + delta                  # add the lag back
        out.append(nxt)
        hist.append(nxt)
    return np.array(out)
