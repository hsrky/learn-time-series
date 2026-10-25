import numpy as np


def ols_reconcile(S, y_hat):
    """Return {"bottom": [...], "all": [...]} with coherent forecasts."""
    raise NotImplementedError


def is_coherent(S, y, tol=1e-9):
    """True if y equals S @ (last m entries of y)."""
    raise NotImplementedError
