import numpy as np
import pandas as pd


def monthly_clip_lag(df, lo=0, hi=20):
    """Monthly sum per (month, shop, item), clipped to [lo, hi], plus the previous month's value as lag_1."""
    raise NotImplementedError
