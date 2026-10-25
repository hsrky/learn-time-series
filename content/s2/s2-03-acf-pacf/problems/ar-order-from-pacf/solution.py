import numpy as np


def _last_significant(vals, band):
    v = np.abs(np.asarray(vals, dtype=float)[1:])    # skip lag 0
    idx = np.nonzero(v > band)[0]                    # strict "greater than"
    return int(idx[-1]) + 1 if len(idx) else 0       # +1 because lag 0 was skipped


def suggest_orders(acf_vals, pacf_vals, n):
    band = 1.96 / np.sqrt(n)
    p = _last_significant(pacf_vals, band)
    q = _last_significant(acf_vals, band)
    if p == 0 and q == 0:
        model = "white noise"
    elif q == 0:
        model = f"AR({p})"
    elif p == 0:
        model = f"MA({q})"
    elif p < q:
        model = f"AR({p})"
    elif q < p:
        model = f"MA({q})"
    else:
        model = "ARMA"
    return {"p": p, "q": q, "model": model}
