import pandas as pd


def upsert_forecasts(existing, new):
    """Merge `new` into `existing` by key (date, series_id); new rows win."""
    key = ["date", "series_id"]
    parts = [d for d in (existing, new) if len(d)]          # skip empty tables
    if not parts:
        return existing.reset_index(drop=True)
    both = pd.concat(parts, ignore_index=True)              # old rows first, new rows last
    both = both.drop_duplicates(subset=key, keep="last")   # the newest row per key survives
    return both.sort_values(key).reset_index(drop=True)
