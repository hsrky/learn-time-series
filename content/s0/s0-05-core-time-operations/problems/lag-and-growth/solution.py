import pandas as pd


def lag_table(s):
    """Return a DataFrame: sales, lag1, change, growth, avg3_before."""
    s = s.astype(float)
    lag1 = s.shift(1)                                # yesterday
    change = s - lag1                                # today minus yesterday
    growth = change / lag1                           # relative change
    avg3_before = s.rolling(3).mean().shift(1)       # mean of 3 previous rows, today excluded
    return pd.DataFrame({"sales": s, "lag1": lag1, "change": change,
                         "growth": growth, "avg3_before": avg3_before})
