import numpy as np
import pandas as pd


def weekly_wape(df):
    """WAPE per group and Monday-start week. NaN when the actual sum is 0."""
    if len(df) == 0:
        return pd.DataFrame({"group": [], "week_start": pd.to_datetime([]), "wape": []})
    d = df.copy()
    day = d["date"].dt.normalize()
    d["week_start"] = day - pd.to_timedelta(day.dt.weekday, unit="D")   # Monday of that week
    d["abs_err"] = (d["actual"] - d["forecast"]).abs()
    g = d.groupby(["group", "week_start"], as_index=False)[["abs_err", "actual"]].sum()
    g["wape"] = (g["abs_err"] / g["actual"]).where(g["actual"] > 0, np.nan)
    return g[["group", "week_start", "wape"]].sort_values(["group", "week_start"]).reset_index(drop=True)
