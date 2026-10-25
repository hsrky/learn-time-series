import numpy as np
import pandas as pd


def difference(s, m=0, d=0):
    out = s.astype(float)
    if m > 0:
        out = out.diff(m)          # y[t] - y[t-m]; first m values become NaN
    for _ in range(d):
        out = out.diff(1)          # y[t] - y[t-1]; one more NaN each time
    if m == 0 and d == 0:
        return s
    return out.dropna()
