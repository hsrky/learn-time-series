import numpy as np


def mask_spikes(x, limit):
    """Return (clean, n): spikes (> limit) replaced by nan, and how many there were."""
    x = np.asarray(x)
    mask = x > limit                     # True at spikes; nan > limit is False
    clean = x.astype(float).copy()       # copy so the input is not changed
    clean[mask] = np.nan
    return clean, int(mask.sum())
