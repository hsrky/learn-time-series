import numpy as np


def box_cox(y, lam):
    y = np.asarray(y, dtype=float)
    if np.any(y <= 0):
        raise ValueError("Box-Cox needs positive values")
    if lam == 0:
        return np.log(y)                    # limit case: the natural log
    return (y ** lam - 1.0) / lam


def inv_box_cox(w, lam):
    w = np.asarray(w, dtype=float)
    if lam == 0:
        return np.exp(w)
    return (lam * w + 1.0) ** (1.0 / lam)
