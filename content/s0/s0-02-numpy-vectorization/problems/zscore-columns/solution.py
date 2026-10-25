import numpy as np


def zscore_columns(data):
    """Return the z-score of each column of data, ignoring nan."""
    data = np.asarray(data, dtype=float)
    mean = np.nanmean(data, axis=0)          # one mean per column
    std = np.nanstd(data, axis=0)            # one std per column
    safe = np.where(std == 0, 1.0, std)      # avoid dividing by zero
    return (data - mean) / safe              # broadcasting (n, m) with (m,)
