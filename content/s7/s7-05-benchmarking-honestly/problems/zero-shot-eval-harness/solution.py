import numpy as np


def _mase(test, fc, scale):
    return float(np.mean(np.abs(test - fc)) / scale)


def evaluate_models(train_list, test_list, forecasts, season):
    """Return {name: {"mase": float, "rel_mase": float}} plus "seasonal_naive"."""
    names = list(forecasts)
    mases = {n: [] for n in names + ["seasonal_naive"]}
    rels = {n: [] for n in names + ["seasonal_naive"]}
    for i, (train, test) in enumerate(zip(train_list, test_list)):
        train = np.asarray(train, float)
        test = np.asarray(test, float)
        if len(train) <= season:
            continue                                   # no seasonal scale available
        scale = np.mean(np.abs(train[season:] - train[:-season]))
        if scale == 0:
            continue                                   # MASE undefined
        snaive = np.resize(train[-season:], len(test))  # repeat the last season
        base = _mase(test, snaive, scale)
        if base == 0:
            continue                                   # ratio would divide by zero
        mases["seasonal_naive"].append(base)
        rels["seasonal_naive"].append(1.0)
        for n in names:
            m = _mase(test, np.asarray(forecasts[n][i], float), scale)
            mases[n].append(m)
            rels[n].append(max(m / base, 1e-12))
    out = {}
    for n in mases:
        if not mases[n]:
            out[n] = {"mase": float("nan"), "rel_mase": float("nan")}
        else:
            out[n] = {"mase": float(np.mean(mases[n])),
                      "rel_mase": float(np.exp(np.mean(np.log(rels[n]))))}
    return out
