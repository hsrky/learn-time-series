import pandas as pd


def point_in_time_join(labels, features, tolerance=None):
    """Attach the latest feature values known at or before each label time.

    labels: columns entity, ts, label
    features: columns entity, feature_ts, <feature columns>
    tolerance: None or pd.Timedelta (maximum age of a feature value)
    Return labels columns + feature columns (no feature_ts), same row order, index 0..n-1.
    """
    raise NotImplementedError
