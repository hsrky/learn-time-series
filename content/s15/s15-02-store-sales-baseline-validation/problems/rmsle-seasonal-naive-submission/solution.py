import numpy as np
import pandas as pd


def rmsle(y_true, y_pred):
    """Root mean squared logarithmic error; negative predictions are clipped to 0."""
    t = np.asarray(y_true, dtype=float)
    p = np.clip(np.asarray(y_pred, dtype=float), 0, None)
    return float(np.sqrt(np.mean((np.log1p(p) - np.log1p(t)) ** 2)))


def seasonal_naive_forecast(train, test_dates, season=7):
    """Forecast each (store_nbr, family) series with the value from the last `season` days.
    Return columns store_nbr, family, date, sales."""
    last = train["date"].max()
    series = train[["store_nbr", "family"]].drop_duplicates()
    dates = pd.DataFrame({"date": pd.to_datetime(list(test_dates))})
    t = series.merge(dates, how="cross")
    steps = np.ceil((t["date"] - last).dt.days / season).astype(int)      # seasons to go back
    t["src_date"] = t["date"] - pd.to_timedelta(steps * season, unit="D")
    src = train[["store_nbr", "family", "date", "sales"]].rename(columns={"date": "src_date"})
    t = t.merge(src, on=["store_nbr", "family", "src_date"], how="left")
    t["sales"] = t["sales"].fillna(0.0)
    out = t[["store_nbr", "family", "date", "sales"]]
    return out.sort_values(["store_nbr", "family", "date"]).reset_index(drop=True)
