import numpy as np


def leaderboard(train, test, m):
    train = np.asarray(train, dtype=float)
    test = np.asarray(test, dtype=float)
    n, h = len(train), len(test)
    j = np.arange(1, h + 1)

    forecasts = {
        "mean": np.full(h, train.mean()),
        "naive": np.full(h, train[-1]),
    }
    if n >= m:
        forecasts["seasonal_naive"] = train[n - m + (j - 1) % m]
    forecasts["drift"] = train[-1] + j * (train[-1] - train[0]) / (n - 1)

    maes = {k: float(np.mean(np.abs(test - f))) for k, f in forecasts.items()}
    best = min(maes, key=maes.get)                   # first minimum in dict order
    skill = 0.0 if maes["naive"] == 0 else 1 - maes[best] / maes["naive"]
    return {"mae": {k: round(v, 4) for k, v in maes.items()}, "best": best, "skill": round(skill, 4)}
