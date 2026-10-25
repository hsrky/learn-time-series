import numpy as np
import pandas as pd


class PerSeriesScaler:
    def __init__(self, log=True):
        self.log = log
        self.mu = {}
        self.sd = {}

    def _v(self, y):
        y = np.asarray(y, dtype=float)
        return np.log1p(y) if self.log else y

    def fit(self, df, cutoff):
        """Learn mu and sd per series from rows with date < cutoff."""
        train = df[pd.to_datetime(df["date"]) < pd.Timestamp(cutoff)]
        self.mu, self.sd = {}, {}
        for sid in df["series_id"].unique():            # unseen-in-train series get identity
            self.mu[sid], self.sd[sid] = 0.0, 1.0
        tmp = pd.DataFrame({"series_id": train["series_id"].values, "v": self._v(train["y"].values)})
        stats = tmp.groupby("series_id")["v"].agg(["mean", lambda s: s.std(ddof=0)])
        for sid, (m, s) in stats.iterrows():
            self.mu[sid] = float(m)
            self.sd[sid] = float(s) if s > 0 else 1.0   # constant series -> sd = 1
        return self

    def _params(self, ids):
        mu = np.array([self.mu.get(i, 0.0) for i in ids], dtype=float)
        sd = np.array([self.sd.get(i, 1.0) for i in ids], dtype=float)
        return mu, sd

    def transform(self, df):
        """Return a Series of scaled values aligned with df."""
        mu, sd = self._params(df["series_id"].tolist())
        return pd.Series((self._v(df["y"].values) - mu) / sd, index=df.index)

    def inverse_transform(self, series_ids, z):
        """Return values in original units as a numpy array."""
        mu, sd = self._params(list(series_ids))
        v = np.asarray(z, dtype=float) * sd + mu        # undo standardization first
        return np.maximum(np.expm1(v), 0.0) if self.log else v   # then undo the log
