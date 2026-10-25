import pandas as pd


def time_split(df, cutoff, gap_days=0):
    """Return (train, test) split by time. See the problem statement."""
    df = df.sort_index()                      # oldest first
    cutoff = pd.Timestamp(cutoff)
    limit = cutoff - pd.Timedelta(days=gap_days)   # train must end before this date
    train = df[df.index < limit]              # strictly before the limit
    test = df[df.index >= cutoff]             # the cutoff day belongs to the test set
    return train, test
