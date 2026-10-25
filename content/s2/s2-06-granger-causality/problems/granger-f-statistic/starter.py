import numpy as np


def granger_f(y, x, p):
    """F statistic for 'x Granger-causes y' with p lags."""
    raise NotImplementedError


def granger_direction(x, y, p, crit):
    """Return 'x->y', 'y->x', 'both' or 'none' by comparing both F statistics with crit."""
    raise NotImplementedError
