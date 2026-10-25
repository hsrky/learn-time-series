import pandas as pd


def sessionize_df(df):
    d = df.sort_values(["user", "ts"]).reset_index(drop=True)
    gap = d.groupby("user")["ts"].diff()
    new = gap.isna() | (gap > pd.Timedelta(minutes=30))              # True at the first event of a session
    d["session"] = new.groupby(d["user"]).cumsum().astype(int)
    out = (d.groupby(["user", "session"])["ts"]
             .agg(start="min", end="max", events="size")
             .reset_index())
    return out[["user", "session", "start", "end", "events"]]
