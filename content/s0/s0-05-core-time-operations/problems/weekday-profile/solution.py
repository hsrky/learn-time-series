import pandas as pd


def weekday_profile(s):
    """Return the mean of s for each weekday 0 (Mon) .. 6 (Sun)."""
    by_day = s.groupby(s.index.dayofweek).mean()   # average of all Mondays, all Tuesdays, ...
    return by_day.reindex(range(7))                # always 7 rows, NaN if a weekday is absent
