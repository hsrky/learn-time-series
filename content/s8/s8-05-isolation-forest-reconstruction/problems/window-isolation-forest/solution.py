import numpy as np
from sklearn.ensemble import IsolationForest


def window_isolation_forest(values, w, k):
    x = np.asarray(values, dtype=float)
    W = np.array([x[i:i + w] for i in range(len(x) - w + 1)])      # one row per window
    F = np.c_[W.mean(axis=1), W.std(axis=1), W.max(axis=1) - W.min(axis=1)]
    iso = IsolationForest(n_estimators=100, random_state=0).fit(F)
    scores = iso.score_samples(F)                                    # lower = more abnormal
    worst = np.argsort(scores, kind="stable")[:k]
    return sorted(int(i) for i in worst)
