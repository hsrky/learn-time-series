import numpy as np
import pandas as pd


def holiday_features(dates, holidays, before=0, after=0):
    idx = pd.DatetimeIndex(dates)
    days = idx.normalize()                                   # compare calendar days only
    out = pd.DataFrame(index=idx)
    for name, date_list in holidays.items():
        marked = set()
        for d in date_list:
            h = pd.Timestamp(d).normalize()
            window = pd.date_range(h - pd.Timedelta(days=before), h + pd.Timedelta(days=after), freq="D")
            marked.update(window)
        out[name] = days.isin(list(marked)).astype(int)
    if len(holidays):
        out["any_holiday"] = out[list(holidays)].max(axis=1).astype(int)
    else:
        out["any_holiday"] = 0
    return out
