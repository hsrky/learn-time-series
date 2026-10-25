import pandas as pd


def point_in_time_join(labels, features, tolerance=None):
    """Attach the latest feature values known at or before each label time."""
    left = labels.copy()
    left["_row"] = range(len(left))          # remember the original order
    left = left.sort_values("ts", kind="stable")
    right = features.sort_values("feature_ts", kind="stable")
    out = pd.merge_asof(left, right, left_on="ts", right_on="feature_ts",
                        by="entity", direction="backward", tolerance=tolerance)
    out = out.sort_values("_row").drop(columns=["_row", "feature_ts"])
    return out.reset_index(drop=True)
