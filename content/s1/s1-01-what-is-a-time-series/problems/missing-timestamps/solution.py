import pandas as pd


def missing_timestamps(index, freq):
    """Return the missing times (as 'YYYY-MM-DD HH:MM' strings) between the first and last time."""
    index = pd.DatetimeIndex(index)
    if len(index) == 0:
        return []
    full = pd.date_range(index.min(), index.max(), freq=freq)   # the complete calendar
    missing = full.difference(index)                            # sorted; ignores duplicates
    return list(missing.strftime("%Y-%m-%d %H:%M"))
