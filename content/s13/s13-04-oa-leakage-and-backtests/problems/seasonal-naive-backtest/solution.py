def seasonal_naive_backtest(y, m, h, k):
    """MAE of a seasonal naive forecast over k folds of horizon h (last k*h points are tested)."""
    n = len(y)
    total = 0.0
    for j in range(k):
        o = n - (k - j) * h                       # forecast origin: train on y[:o]
        for i in range(h):
            pred = y[o - m + (i % m)]             # repeat the last season
            total += abs(y[o + i] - pred)
    return total / (k * h)
