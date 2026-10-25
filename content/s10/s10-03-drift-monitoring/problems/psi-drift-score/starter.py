import numpy as np


def psi(expected, actual, bins=10, eps=1e-4):
    """Population Stability Index of `actual` against `expected`.

    Inner edges = quantiles of `expected` at k/bins (k = 1..bins-1).
    Bin of x = np.searchsorted(inner, x, side="right"). Shares are clipped to >= eps.
    Return sum((a - e) * ln(a / e)) as a float.
    """
    raise NotImplementedError
