import numpy as np


def rolling_zscore_anomalies(values, window, threshold):
    x = np.asarray(values, dtype=float)
    out = []
    for i in range(window, len(x)):
        w = x[i - window:i]              # past values only
        mean = w.mean()
        std = w.std()                    # population std
        if std < 1e-9:
            if x[i] != mean:             # flat window: any change is an anomaly
                out.append(i)
        elif abs(x[i] - mean) / std > threshold:
            out.append(i)
    return out
