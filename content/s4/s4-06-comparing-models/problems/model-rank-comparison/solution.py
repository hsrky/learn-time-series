import numpy as np
import pandas as pd


def compare_models(errors, baseline):
    """Return a DataFrame with columns avg_rank and rel_error, one row per model."""
    # 1) average rank: rank inside each row, ties -> average rank, NaN stays NaN
    avg_rank = errors.rank(axis=1, method="average").mean(axis=0)

    # 2) relative error against the baseline, geometric mean over series
    base = errors[baseline]
    keep = base.notna() & (base != 0)               # skip unusable series
    ratio = errors[keep].div(base[keep], axis=0)
    with np.errstate(divide="ignore"):
        log_ratio = np.log(ratio)                   # log(0) = -inf -> geometric mean 0
    rel = np.exp(log_ratio.mean(axis=0, skipna=True))
    out = pd.DataFrame({"avg_rank": avg_rank, "rel_error": rel})
    return out.loc[errors.columns]
