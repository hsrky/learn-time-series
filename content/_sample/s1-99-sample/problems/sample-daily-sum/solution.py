import pandas as pd


def daily_total(s: pd.Series) -> pd.Series:
    """Return the sum of each calendar day."""
    return s.resample("D").sum()
