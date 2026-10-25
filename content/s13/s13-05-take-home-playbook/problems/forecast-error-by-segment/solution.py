import numpy as np
import pandas as pd


def error_by_segment(df):
    """Per segment: n, wape, bias, share_of_error; sorted by share_of_error desc, then segment."""
    cols = ["segment", "n", "wape", "bias", "share_of_error"]
    if len(df) == 0:
        return pd.DataFrame({c: [] for c in cols})
    d = df.assign(abs_err=(df["actual"] - df["forecast"]).abs(),
                  signed=df["forecast"] - df["actual"])
    g = d.groupby("segment", as_index=False).agg(
        n=("actual", "size"), abs_err=("abs_err", "sum"),
        signed=("signed", "sum"), actual=("actual", "sum"))
    pos = g["actual"] > 0
    g["wape"] = (g["abs_err"] / g["actual"]).where(pos, np.nan)
    g["bias"] = (g["signed"] / g["actual"]).where(pos, np.nan)
    total = g["abs_err"].sum()
    g["share_of_error"] = g["abs_err"] / total if total > 0 else 0.0
    g = g.sort_values(["share_of_error", "segment"], ascending=[False, True])
    return g[cols].reset_index(drop=True)
