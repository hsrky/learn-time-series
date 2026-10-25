import numpy as np


def point_metrics(y_true, y_pred):
    """Return {"mae", "rmse", "mape", "smape", "wape"}. See the statement for edge cases."""
    y = np.asarray(y_true, dtype=float)
    f = np.asarray(y_pred, dtype=float)
    if len(y) == 0:
        return {k: float("nan") for k in ("mae", "rmse", "mape", "smape", "wape")}
    e = np.abs(y - f)
    mae = e.mean()
    rmse = np.sqrt(((y - f) ** 2).mean())

    nz = y != 0                                   # MAPE: skip zero actuals
    mape = (e[nz] / np.abs(y[nz])).mean() * 100 if nz.any() else float("nan")

    denom = np.abs(y) + np.abs(f)
    terms = np.zeros_like(e)                      # both zero -> error 0
    ok = denom != 0
    terms[ok] = 2 * e[ok] / denom[ok]
    smape = terms.mean() * 100

    total = np.abs(y).sum()
    wape = e.sum() / total if total != 0 else float("nan")
    return {"mae": float(mae), "rmse": float(rmse), "mape": float(mape),
            "smape": float(smape), "wape": float(wape)}
