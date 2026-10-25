import pandas as pd


def hours_in_day(date, tz):
    """Return how many real hours the local calendar day `date` has in zone `tz`."""
    day = pd.Timestamp(date)                              # naive midnight
    start = day.tz_localize(tz)                           # local midnight
    end = (day + pd.Timedelta(days=1)).tz_localize(tz)    # next local midnight
    return int(round((end - start).total_seconds() / 3600))
