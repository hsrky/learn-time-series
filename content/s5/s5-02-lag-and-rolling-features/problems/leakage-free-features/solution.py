import numpy as np
import pandas as pd


def build_features(df):
    """Return the feature table described in the problem statement."""
    out = df.sort_values(["series_id", "date"]).reset_index(drop=True)[["series_id", "date", "y"]]
    g = out.groupby("series_id")["y"]
    out["lag_1"] = g.shift(1)
    out["lag_7"] = g.shift(7)
    # shift first (drop the current row), then roll, all inside each series
    out["roll_mean_3"] = g.transform(lambda s: s.shift(1).rolling(3).mean())
    out["roll_std_3"] = g.transform(lambda s: s.shift(1).rolling(3).std(ddof=1))
    out["exp_mean"] = g.transform(lambda s: s.shift(1).expanding().mean())
    return out
