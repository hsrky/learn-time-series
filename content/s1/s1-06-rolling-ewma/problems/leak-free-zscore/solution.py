import numpy as np
import pandas as pd


def rolling_zscore(s, window):
    """z-score of each value against the `window` values BEFORE it."""
    past = s.shift(1)                              # row t now holds s[t-1]
    mean = past.rolling(window).mean()             # windows end at t-1: today is not inside
    std = past.rolling(window).std()               # sample std (ddof=1)
    std = std.where(std > 0)                       # std == 0 -> NaN
    return (s - mean) / std
