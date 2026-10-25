import warnings

import numpy as np
from statsmodels.tsa.stattools import adfuller, kpss


def unit_root_verdict(x, alpha=0.05):
    x = np.asarray(x, dtype=float)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")                    # KPSS interpolation warning
        adf_p = adfuller(x, regression="c", autolag="AIC")[1]
        kpss_p = kpss(x, regression="c", nlags="auto")[1]
    adf_rejects = adf_p < alpha        # ADF H0 = unit root  -> reject means stationary
    kpss_rejects = kpss_p < alpha      # KPSS H0 = stationary -> reject means NOT stationary
    if adf_rejects and not kpss_rejects:
        verdict = "stationary"
    elif not adf_rejects and kpss_rejects:
        verdict = "unit root"
    elif adf_rejects and kpss_rejects:
        verdict = "mixed"
    else:
        verdict = "inconclusive"
    return {"adf_p": round(float(adf_p), 4), "kpss_p": round(float(kpss_p), 4), "verdict": verdict}


def suggest_d(x, max_d=2, alpha=0.05):
    x = np.asarray(x, dtype=float)
    for d in range(max_d + 1):
        if unit_root_verdict(x, alpha)["verdict"] == "stationary":
            return d
        x = np.diff(x)                                     # one more difference
    return max_d
