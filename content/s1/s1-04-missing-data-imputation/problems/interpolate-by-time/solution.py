import numpy as np
import pandas as pd


def interpolate_by_time(s):
    """Fill inner NaN by linear interpolation over real time. Edge NaN stay NaN."""
    x = s.index.asi8.astype(float)             # time as numbers (nanoseconds)
    y = s.to_numpy(dtype=float)
    ok = ~np.isnan(y)
    if not ok.any():
        return s.copy()
    out = y.copy()
    miss = ~ok
    out[miss] = np.interp(x[miss], x[ok], y[ok])       # straight line between valid neighbors
    outside = miss & ((x < x[ok][0]) | (x > x[ok][-1]))
    out[outside] = np.nan                               # no extrapolation at the edges
    return pd.Series(out, index=s.index, name=s.name)
