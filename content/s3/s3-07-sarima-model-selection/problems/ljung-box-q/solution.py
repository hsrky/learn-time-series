import numpy as np


def ljung_box(resid, nlags, n_params=0):
    x = np.asarray(resid, dtype=float)
    n = len(x)
    d = x - x.mean()
    denom = float(d @ d)
    df = nlags - n_params
    if denom == 0:
        return {"q": 0.0, "df": df}
    r = np.array([np.sum(d[k:] * d[:n - k]) / denom for k in range(1, nlags + 1)])
    k = np.arange(1, nlags + 1)
    q = n * (n + 2) * np.sum(r ** 2 / (n - k))
    return {"q": float(q), "df": int(df)}
