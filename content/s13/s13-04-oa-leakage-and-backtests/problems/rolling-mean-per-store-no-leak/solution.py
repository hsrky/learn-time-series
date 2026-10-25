import pandas as pd


def prev_rolling_mean(df, window):
    """Mean sales of up to `window` earlier days of the same store (today excluded).
    Return a Series with the same index as df."""
    d = df.sort_values(["store", "date"])
    feat = d.groupby("store")["sales"].transform(
        lambda s: s.shift(1).rolling(window, min_periods=1).mean()   # shift first: no leak
    )
    return feat.reindex(df.index).astype(float)
