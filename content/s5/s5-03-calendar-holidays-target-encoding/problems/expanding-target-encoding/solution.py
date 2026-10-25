import numpy as np
import pandas as pd


def expanding_target_encoding(df, cat, target, m=0.0):
    """Return a Series with the time-safe, smoothed target encoding of `cat`."""
    y = df[target].astype(float)
    n = len(df)
    g = df.groupby(cat)[target]
    prev_sum = g.cumsum().astype(float) - y            # earlier sum in the same category
    prev_cnt = g.cumcount().astype(float)              # earlier count in the same category
    with np.errstate(divide="ignore", invalid="ignore"):
        prior = (y.cumsum() - y) / np.arange(n)        # mean of all earlier rows (NaN at row 0)
        smooth = (prev_sum + m * prior) / (prev_cnt + m)
    out = smooth.where((prev_cnt + m) > 0, prior)      # new category and m == 0 -> prior
    out[prior.isna()] = np.nan                         # first row has nothing to learn from
    return out
