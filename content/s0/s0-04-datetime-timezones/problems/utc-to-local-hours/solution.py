import pandas as pd


def local_hours(timestamps, tz):
    """Return the local hour of day (0-23) for each UTC timestamp string."""
    idx = pd.to_datetime(list(timestamps))      # naive DatetimeIndex
    if len(idx) == 0:
        return []
    local = idx.tz_localize("UTC").tz_convert(tz)   # label as UTC, then change the clock
    return [int(h) for h in local.hour]
