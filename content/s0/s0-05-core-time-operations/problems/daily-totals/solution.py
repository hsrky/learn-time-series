import pandas as pd


def daily_totals(s):
    """Return the total per calendar day of an hourly Series."""
    # resample groups by calendar day; sum() skips NaN and gives 0.0 for empty days
    return s.resample("D").sum()
