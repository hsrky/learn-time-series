import numpy as np
import pandas as pd


def wap(bid_price1, ask_price1, bid_size1, ask_size1):
    """Weighted average price of the best bid and ask."""
    bp, ap = np.asarray(bid_price1, dtype=float), np.asarray(ask_price1, dtype=float)
    bs, as_ = np.asarray(bid_size1, dtype=float), np.asarray(ask_size1, dtype=float)
    return (bp * as_ + ap * bs) / (bs + as_)


def realized_volatility(book):
    """DataFrame time_id, rv: sqrt of the sum of squared WAP log returns inside each time_id."""
    if len(book) == 0:
        return pd.DataFrame({"time_id": [], "rv": []})
    d = book.sort_values(["time_id", "seconds_in_bucket"]).copy()
    d["log_wap"] = np.log(wap(d["bid_price1"], d["ask_price1"], d["bid_size1"], d["ask_size1"]))
    d["ret2"] = d.groupby("time_id")["log_wap"].diff() ** 2        # first row of a window is NaN
    out = d.groupby("time_id")["ret2"].sum().pow(0.5).rename("rv").reset_index()
    return out.sort_values("time_id").reset_index(drop=True)
