import numpy as np


def top_down(history, total_forecast, method="avg_of_props"):
    H = np.asarray(history, dtype=float)
    total = H.sum(axis=1)                                # total of each period
    if method == "avg_of_props":
        p = (H / total[:, None]).mean(axis=0)            # mean of the period shares
    elif method == "prop_of_avgs":
        p = H.mean(axis=0) / total.mean()                # share of the mean levels
    else:
        raise ValueError("unknown method")
    return np.outer(np.asarray(total_forecast, dtype=float), p)
