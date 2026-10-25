import numpy as np


def make_windows(series, input_len, horizon, stride=1):
    """Return (X, y). X: [n, input_len, features], y: [n, horizon] (column 0)."""
    raise NotImplementedError
