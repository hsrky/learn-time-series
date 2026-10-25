import numpy as np
import pandas as pd


def top_anomalous_days(s, k):
    """Dates (YYYY-MM-DD strings) of the k days with the highest robust weekday-adjusted score."""
    if len(s) == 0:
        return []
    s = s.sort_index()
    expected = s.groupby(s.index.dayofweek).transform("median")   # same weekday median
    resid = s - expected
    med = resid.median()
    dev = (resid - med).abs()
    mad = dev.median()
    score = dev / mad if mad > 0 else dev
    order = score.sort_values(ascending=False, kind="stable")       # stable: earlier date wins ties
    return [d.strftime("%Y-%m-%d") for d in order.index[:k]]
