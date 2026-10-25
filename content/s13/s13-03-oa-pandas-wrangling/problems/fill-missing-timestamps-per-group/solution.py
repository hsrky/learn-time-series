import pandas as pd


def fill_missing_days(df):
    """Add a row with sales 0 for each missing day between a store's first and last date."""
    parts = []
    for store, g in df.groupby("store"):
        s = g.set_index("date")["sales"].sort_index()
        full = pd.date_range(s.index.min(), s.index.max(), freq="D")
        s = s.reindex(full, fill_value=0)          # new days get 0
        parts.append(pd.DataFrame({"store": store, "date": full, "sales": s.to_numpy()}))
    if not parts:
        return pd.DataFrame({"store": [], "date": pd.to_datetime([]), "sales": []})
    out = pd.concat(parts, ignore_index=True)
    return out.sort_values(["store", "date"]).reset_index(drop=True)
