import numpy as np


def _trim(c):
    c = list(c)
    while c and c[-1] == 0:
        c.pop()                                  # trailing zeros do not change the model
    return c


def _roots_outside(poly_increasing):
    # poly_increasing = [a0, a1, ..., ak] for a0 + a1 z + ... + ak z^k
    if len(poly_increasing) <= 1:
        return True                              # no roots: white noise
    roots = np.roots(poly_increasing[::-1])      # np.roots wants the highest power first
    return bool(np.all(np.abs(roots) > 1 + 1e-9))


def ma_invertible(theta):
    return _roots_outside([1.0] + [float(t) for t in _trim(theta)])


def ar_stationary(phi):
    return _roots_outside([1.0] + [-float(p) for p in _trim(phi)])
