import pandas as pd


def direct_dataset(s, n_lags, h):
    """Return DataFrame with lag_0..lag_{n_lags-1} and target = s shifted by -h; drop NaN rows."""
    cols = {f"lag_{j}": s.shift(j) for j in range(n_lags)}   # past values only
    cols["target"] = s.shift(-h)                              # the future value, used only as the answer
    return pd.DataFrame(cols).dropna()
