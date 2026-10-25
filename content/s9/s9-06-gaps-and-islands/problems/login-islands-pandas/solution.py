import pandas as pd


def login_islands(df):
    d = df.drop_duplicates().sort_values(["user", "day"]).reset_index(drop=True)
    row = d.groupby("user").cumcount()                      # 0, 1, 2, ... per user
    d["key"] = d["day"] - pd.to_timedelta(row, unit="D")    # constant inside an island
    out = (d.groupby(["user", "key"])["day"]
             .agg(start="min", end="max", days="size")
             .reset_index()
             .drop(columns="key")
             .sort_values(["user", "start"])
             .reset_index(drop=True))
    return out[["user", "start", "end", "days"]]
