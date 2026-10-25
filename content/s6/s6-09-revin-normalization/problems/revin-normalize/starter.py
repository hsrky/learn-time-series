import numpy as np


def revin_normalize(x, gamma, beta, eps=1e-5):
    """Return (xn, mean, std). Shapes: x [B, T, C]; mean, std [B, 1, C]."""
    raise NotImplementedError


def revin_denormalize(y, mean, std, gamma, beta):
    """Undo the normalization on model output y [B, H, C]."""
    raise NotImplementedError
