import pandas as pd


def attach_latest(a, b, tol_seconds):
    """For each row of a, attach the latest humidity of the same device that is not in the future
    and not older than tol_seconds. Return device, time, temp, humidity sorted by device, time."""
    left = a.sort_values("time", kind="stable")
    right = b.sort_values("time", kind="stable")
    out = pd.merge_asof(
        left, right, on="time", by="device",
        tolerance=pd.Timedelta(seconds=tol_seconds),
        direction="backward",               # never look at the future
    )
    out = out[["device", "time", "temp", "humidity"]]
    return out.sort_values(["device", "time"], kind="stable").reset_index(drop=True)
