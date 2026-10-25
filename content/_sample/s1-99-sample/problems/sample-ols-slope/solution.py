import numpy as np
import statsmodels.api as sm


def slope(y):
    """Return the OLS slope of y against 0..n-1."""
    y = np.asarray(y, dtype=float)
    X = sm.add_constant(np.arange(len(y), dtype=float))
    return float(sm.OLS(y, X).fit().params[1])
