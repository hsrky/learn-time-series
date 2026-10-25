import numpy as np
import pandas as pd


def hierarchy_weights(bottom, levels):
    """Revenue-share weights for each group of each level. Columns: level, key, weight."""
    total = float(bottom["revenue"].sum())
    parts = []
    for i, cols in enumerate(levels):
        if len(cols) == 0:
            parts.append(pd.DataFrame({"level": [i], "key": ["Total"], "revenue": [total]}))
            continue
        g = bottom.groupby(list(cols), as_index=False)["revenue"].sum()
        g["key"] = g[list(cols)].astype(str).agg("/".join, axis=1)
        g["level"] = i
        parts.append(g[["level", "key", "revenue"]])
    out = pd.concat(parts, ignore_index=True)
    out["weight"] = out["revenue"] / total if total > 0 else 0.0
    out = out[["level", "key", "weight"]]
    return out.sort_values(["level", "key"]).reset_index(drop=True)


def rmsse(train, actual, forecast):
    """Root mean squared scaled error; the scale starts at the first non-zero training value."""
    y = np.asarray(train, dtype=float)
    nz = np.nonzero(y)[0]
    if len(nz) == 0:
        return float("nan")
    y = y[nz[0]:]
    if len(y) < 2:
        return float("nan")
    scale = np.mean(np.diff(y) ** 2)
    if scale == 0:
        return float("nan")
    err = np.mean((np.asarray(actual, dtype=float) - np.asarray(forecast, dtype=float)) ** 2)
    return float(np.sqrt(err / scale))
