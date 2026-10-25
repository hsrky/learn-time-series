import numpy as np
import pandas as pd


def pit_join(events, features, tolerance_hours=None):
    """Attach the latest feature value known at each event time (same id)."""
    ev = events.copy()
    ev["_row"] = np.arange(len(ev))                   # remember the original order
    left = ev.sort_values("time", kind="stable")
    right = (features.rename(columns={"available_at": "feature_time", "value": "feature_value"})
             .sort_values("feature_time", kind="stable"))
    if len(right) == 0:                               # nothing to join
        out = left.copy()
        out["feature_time"] = pd.NaT
        out["feature_value"] = np.nan
    else:
        tol = None if tolerance_hours is None else pd.Timedelta(hours=tolerance_hours)
        out = pd.merge_asof(left, right[["id", "feature_time", "feature_value"]],
                            left_on="time", right_on="feature_time", by="id",
                            direction="backward", tolerance=tol)
        out.index = left.index                        # merge_asof resets the index
    out = out.sort_values("_row").drop(columns="_row")
    return out
