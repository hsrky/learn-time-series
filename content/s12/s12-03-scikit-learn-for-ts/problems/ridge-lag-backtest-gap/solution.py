import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import TimeSeriesSplit


def backtest_mae(y, n_lags, n_splits, gap):
    y = np.asarray(y, dtype=float)
    # column j holds lag j+1: y[t-1-j]
    X = np.column_stack([y[n_lags - j: len(y) - j] for j in range(1, n_lags + 1)])
    target = y[n_lags:]
    maes = []
    for train_idx, test_idx in TimeSeriesSplit(n_splits=n_splits, gap=gap).split(X):
        model = LinearRegression().fit(X[train_idx], target[train_idx])
        pred = model.predict(X[test_idx])
        maes.append(np.mean(np.abs(pred - target[test_idx])))
    return float(np.mean(maes))
