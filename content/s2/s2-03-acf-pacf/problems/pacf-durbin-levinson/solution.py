import numpy as np


def _acf(x, nlags):
    d = np.asarray(x, dtype=float)
    d = d - d.mean()
    n = len(d)
    denom = np.sum(d * d)
    if denom == 0:
        return None
    return np.array([np.sum(d[k:] * d[:n - k]) / denom for k in range(nlags + 1)])


def pacf(x, nlags):
    r = _acf(x, nlags)
    out = np.zeros(nlags + 1)
    out[0] = 1.0
    if r is None:                               # constant series
        return out
    out[1] = r[1]
    phi = np.array([r[1]])                      # coefficients of the AR(k-1) fit
    for k in range(2, nlags + 1):
        num = r[k] - np.dot(phi, r[1:k][::-1])  # r[k] - sum phi(k-1,j) r[k-j]
        den = 1.0 - np.dot(phi, r[1:k])         # 1 - sum phi(k-1,j) r[j]
        phi_kk = num / den
        phi = np.append(phi - phi_kk * phi[::-1], phi_kk)
        out[k] = phi_kk
    return out
