import numpy as np


def granger_f(y, x, p):
    y = np.asarray(y, dtype=float)
    x = np.asarray(x, dtype=float)
    n = len(y)
    target = y[p:]                                         # y(t), t = p..n-1
    own = [y[p - k:n - k] for k in range(1, p + 1)]        # y(t-k)
    other = [x[p - k:n - k] for k in range(1, p + 1)]      # x(t-k)
    ones = np.ones(n - p)
    Xr = np.column_stack([ones] + own)
    Xu = np.column_stack([ones] + own + other)

    def rss(X):
        beta, *_ = np.linalg.lstsq(X, target, rcond=None)
        r = target - X @ beta
        return float(r @ r)

    rss_r, rss_u = rss(Xr), rss(Xu)
    df2 = (n - p) - (2 * p + 1)
    return ((rss_r - rss_u) / p) / (rss_u / df2)


def granger_direction(x, y, p, crit):
    xy = granger_f(y, x, p) > crit      # does x help to predict y?
    yx = granger_f(x, y, p) > crit      # does y help to predict x?
    if xy and yx:
        return "both"
    if xy:
        return "x->y"
    if yx:
        return "y->x"
    return "none"
