import numpy as np
import pandas as pd


def scale_with_train_stats(df, n_train):
    """Standardize all rows using mean and sd (ddof=0) of the first n_train rows."""
    train = df.iloc[:n_train]
    mu = train.mean()                  # NaN-aware, one number per column
    sd = train.std(ddof=0)
    const = (sd == 0) | sd.isna()      # constant (or all-NaN) training column
    safe_sd = sd.where(~const, 1.0)    # avoid division by zero
    out = (df - mu) / safe_sd
    # Constant columns: every real value becomes 0.0, NaN stays NaN.
    for c in df.columns[const.values]:
        out[c] = out[c].where(df[c].isna(), 0.0)
    return out
