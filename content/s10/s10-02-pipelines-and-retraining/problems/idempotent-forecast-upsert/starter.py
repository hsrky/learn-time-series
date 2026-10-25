import pandas as pd


def upsert_forecasts(existing, new):
    """Merge `new` into `existing` by key (date, series_id); new rows win.

    Columns: date, series_id, yhat, version.
    Return a table sorted by date, series_id with index 0..n-1.
    """
    raise NotImplementedError
