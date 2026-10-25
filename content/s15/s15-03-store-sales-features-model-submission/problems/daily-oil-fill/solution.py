import pandas as pd


def daily_oil(oil, start, end):
    """One oil price per calendar day from start to end: forward fill, then backward fill."""
    start, end = pd.Timestamp(start), pd.Timestamp(end)
    days = pd.date_range(start, end, freq="D")
    s = oil.set_index("date")["dcoilwtico"].sort_index().astype(float)
    if len(s) == 0 or s.notna().sum() == 0:
        return pd.DataFrame({"date": days, "dcoilwtico": float("nan")})
    lo = min(start, s.index.min())
    hi = max(end, s.index.max())
    full = s.reindex(pd.date_range(lo, hi, freq="D"))     # covers dates before `start` too
    full = full.ffill().bfill()
    out = full.loc[start:end]
    return pd.DataFrame({"date": out.index, "dcoilwtico": out.to_numpy()}).reset_index(drop=True)
