import numpy as np


def backtest_splits(n, initial, horizon, step=None, window=None, gap=0):
    """Yield (train_idx, test_idx) numpy arrays for every complete fold."""
    step = horizon if step is None else step
    end = initial                                  # exclusive end of training
    while end + gap + horizon <= n:                # the whole test part must exist
        start = 0 if window is None else max(0, end - window)
        train = np.arange(start, end)
        test = np.arange(end + gap, end + gap + horizon)
        yield train, test
        end += step                                # move the forecast origin
