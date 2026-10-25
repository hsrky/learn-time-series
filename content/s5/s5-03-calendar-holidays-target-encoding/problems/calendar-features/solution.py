import numpy as np
import pandas as pd


def calendar_features(dates, holidays):
    """Return a DataFrame of calendar and holiday-distance features indexed by `dates`."""
    dates = pd.DatetimeIndex(dates)
    hol = pd.DatetimeIndex(pd.to_datetime(list(holidays))).unique().sort_values()
    out = pd.DataFrame(index=dates)
    out["dow"] = dates.dayofweek.astype(int)
    out["is_weekend"] = (dates.dayofweek >= 5).astype(int)
    out["month"] = dates.month.astype(int)
    out["is_holiday"] = dates.isin(hol).astype(int)

    m = len(hol)
    nxt_pos = hol.searchsorted(dates, side="left")      # first holiday >= date
    prv_pos = hol.searchsorted(dates, side="right") - 1  # last holiday <= date
    nxt = np.full(len(dates), np.nan)
    prv = np.full(len(dates), np.nan)
    if m:
        has_next = nxt_pos < m
        nxt[has_next] = (hol[nxt_pos[has_next]] - dates[has_next]).days
        has_prev = prv_pos >= 0
        prv[has_prev] = (dates[has_prev] - hol[prv_pos[has_prev]]).days
    out["days_to_next"] = nxt
    out["days_since_last"] = prv
    return out
