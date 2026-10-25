import numpy as np
import pandas as pd


def causal_fill(s, max_gap):
    """Replace -999 by NaN, build a full daily grid, forward fill at most max_gap days."""
    s = s.replace(-999, np.nan)                                  # hidden missing value
    grid = pd.date_range(s.index.min(), s.index.max(), freq="D")
    s = s.reindex(grid)                                          # add the missing rows
    if max_gap <= 0:
        return s
    return s.ffill(limit=max_gap)                                # past values only, limited length
