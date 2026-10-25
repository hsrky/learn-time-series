import numpy as np
import pandas as pd


def fva_by_step(actual, steps):
    """Return a DataFrame: step, wape, fva_prev, fva_naive, adds_value."""
    a = np.asarray(actual, dtype=float)
    total = a.sum()
    rows = []
    first = prev = None
    for name, f in steps:
        w = float(np.abs(a - np.asarray(f, dtype=float)).sum() / total)   # WAPE of this step
        if first is None:
            fva_prev = fva_naive = 0.0
            adds = False
            first = w
        else:
            fva_prev = prev - w          # positive = this step helped
            fva_naive = first - w
            adds = bool(fva_prev > 1e-12)
        rows.append((name, w, fva_prev, fva_naive, adds))
        prev = w
    return pd.DataFrame(rows, columns=["step", "wape", "fva_prev", "fva_naive", "adds_value"])
