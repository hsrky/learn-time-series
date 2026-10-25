import pandas as pd


def big_sellers(df, min_share):
    """Add a 'share' column and keep rows with share >= min_share."""
    out = df.copy()                              # do not change the input
    out["share"] = out["units"] / out["units"].sum()
    return out[out["share"] >= min_share]        # boolean mask keeps matching rows
