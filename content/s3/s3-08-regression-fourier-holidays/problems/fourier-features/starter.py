import numpy as np


def fourier_features(t, period, K):
    """Return an array of shape (len(t), 2*K) with columns sin1, cos1, sin2, cos2, ..."""
    raise NotImplementedError


def fourier_names(prefix, K):
    """Return ['prefix_sin1', 'prefix_cos1', ..., 'prefix_sinK', 'prefix_cosK']."""
    raise NotImplementedError
