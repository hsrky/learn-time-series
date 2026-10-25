import numpy as np
import pandas as pd


def monthly_clip_lag(df, lo=0, hi=20):
    """Monthly sum per (month, shop, item), clipped to [lo, hi], plus the previous month's value as lag_1."""
    keys = ["date_block_num", "shop_id", "item_id"]
    cols = keys + ["item_cnt_month", "lag_1"]
    if len(df) == 0:
        return pd.DataFrame({c: [] for c in cols})
    m = df.groupby(keys, as_index=False)["item_cnt_day"].sum().rename(columns={"item_cnt_day": "item_cnt_month"})
    m["item_cnt_month"] = m["item_cnt_month"].clip(lo, hi).astype(float)       # clip the monthly sum
    prev = m.rename(columns={"item_cnt_month": "lag_1"}).assign(date_block_num=lambda x: x["date_block_num"] + 1)
    out = m.merge(prev, on=keys, how="left")                                    # previous month, same shop and item
    out["lag_1"] = out["lag_1"].fillna(0.0)
    return out[cols].sort_values(keys).reset_index(drop=True)
