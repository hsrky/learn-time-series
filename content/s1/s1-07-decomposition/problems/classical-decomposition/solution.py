import numpy as np
import pandas as pd


def classical_decompose(s, period, model="additive"):
    """Classical decomposition. Returns a DataFrame: trend, seasonal, resid (same index as s)."""
    y = s.to_numpy(dtype=float)
    n = len(y)
    m = int(period)

    # Step 1: trend = centered moving average of length m.
    # Odd m: all weights 1/m.  Even m (a "2 x m" average): 0.5/m at both ends, 1/m inside.
    if m % 2 == 1:
        w = np.ones(m) / m
    else:
        w = np.r_[0.5, np.ones(m - 1), 0.5] / m
    half = len(w) // 2
    trend = np.full(n, np.nan)                       # the first and last `half` values stay NaN
    trend[half:n - half] = np.convolve(y, w, mode="valid")

    # Step 2: remove the trend (subtract for additive, divide for multiplicative)
    detrended = y - trend if model == "additive" else y / trend

    # Step 3: average the detrended values of each position in the period, skipping NaN
    avg = np.array([np.nanmean(detrended[j::m]) for j in range(m)])
    # center the indexes: additive -> sum 0, multiplicative -> mean 1
    avg = avg - avg.mean() if model == "additive" else avg / avg.mean()
    seasonal = np.tile(avg, n // m + 1)[:n]          # position 0 = first observation

    # Step 4: what is left is the remainder
    resid = y - trend - seasonal if model == "additive" else y / (trend * seasonal)
    return pd.DataFrame({"trend": trend, "seasonal": seasonal, "resid": resid}, index=s.index)
