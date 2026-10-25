import numpy as np


def revin_normalize(x, gamma, beta, eps=1e-5):
    """Return (xn, mean, std). Shapes: x [B, T, C]; mean, std [B, 1, C]."""
    x = np.asarray(x, dtype=float)
    mean = x.mean(axis=1, keepdims=True)              # per sample, per channel
    std = np.sqrt(x.var(axis=1, keepdims=True) + eps)  # population variance + eps
    xn = (x - mean) / std * gamma + beta
    return xn, mean, std


def revin_denormalize(y, mean, std, gamma, beta):
    """Undo the normalization on model output y [B, H, C]."""
    y = np.asarray(y, dtype=float)
    return (y - beta) / gamma * std + mean
