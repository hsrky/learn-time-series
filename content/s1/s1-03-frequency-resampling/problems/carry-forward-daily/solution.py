import pandas as pd


def daily_price(changes, end):
    """Return the daily price from the first change date to `end` (inclusive), carried forward."""
    changes = changes.sort_index()
    calendar = pd.date_range(changes.index[0], end, freq="D")
    # method="ffill": each day takes the latest value at or before it (past only)
    return changes.reindex(calendar, method="ffill")
