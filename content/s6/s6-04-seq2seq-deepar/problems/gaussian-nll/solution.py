import numpy as np


def gaussian_nll(y, mu, sigma, mask=None):
    """Mean negative log-likelihood of y under Normal(mu, sigma^2)."""
    y, mu, sigma = (np.asarray(a, dtype=float) for a in (y, mu, sigma))
    nll = 0.5 * np.log(2 * np.pi * sigma ** 2) + (y - mu) ** 2 / (2 * sigma ** 2)
    if mask is None:
        return float(nll.mean()) if nll.size else 0.0
    mask = np.asarray(mask, dtype=float)
    kept = mask.sum()
    if kept == 0:
        return 0.0
    return float((nll * mask).sum() / kept)   # padded points do not count
