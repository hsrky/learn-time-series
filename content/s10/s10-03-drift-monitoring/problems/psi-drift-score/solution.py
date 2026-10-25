import numpy as np


def psi(expected, actual, bins=10, eps=1e-4):
    """Population Stability Index of `actual` against `expected`."""
    expected = np.asarray(expected, dtype=float)
    actual = np.asarray(actual, dtype=float)
    # fixed inner edges from the training sample
    inner = np.quantile(expected, np.linspace(0, 1, bins + 1)[1:-1])
    # bin index of every value, then the share per bin
    e = np.bincount(np.searchsorted(inner, expected, side="right"), minlength=bins) / len(expected)
    a = np.bincount(np.searchsorted(inner, actual, side="right"), minlength=bins) / len(actual)
    e = np.clip(e, eps, None)      # protect against log(0)
    a = np.clip(a, eps, None)
    return float(np.sum((a - e) * np.log(a / e)))
