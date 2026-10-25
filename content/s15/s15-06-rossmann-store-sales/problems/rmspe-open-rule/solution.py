import numpy as np
import pandas as pd


def rmspe(y_true, y_pred):
    """RMSPE over rows with y_true != 0 (0.0 if there are none)."""
    y = np.asarray(y_true, dtype=float)
    p = np.asarray(y_pred, dtype=float)
    mask = y != 0                                   # closed days are not scored
    if not mask.any():
        return 0.0
    return float(np.sqrt(np.mean(((y[mask] - p[mask]) / y[mask]) ** 2)))


def apply_open_rule(df):
    """0.0 where Open == 0, else pred. A missing Open counts as open."""
    return df["pred"].astype(float).where(df["Open"] != 0, 0.0)
