import numpy as np


def box_cox(y, lam):
    """Box-Cox transform of positive values. Raise ValueError if any value <= 0."""
    raise NotImplementedError


def inv_box_cox(w, lam):
    """Inverse of box_cox."""
    raise NotImplementedError
