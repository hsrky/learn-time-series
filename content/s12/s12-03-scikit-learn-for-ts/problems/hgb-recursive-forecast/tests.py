import numpy as np

def make(seed, n, h, m, amp, sd, level):
    rng = np.random.default_rng(seed)
    t = np.arange(n + h)
    shape = amp * np.sin(2 * np.pi * t / m) + 0.5 * amp * np.sin(2 * np.pi * 3 * t / m)
    y = level + shape + rng.normal(0, sd, n + h)
    return y[:n], y[n:]

TR1, TE1 = make(1, 280, 14, 7, 10, 3.0, 100)
TR2, TE2 = make(2, 240, 12, 12, 8, 2.0, 60)
TR3, TE3 = make(3, 360, 24, 24, 15, 3.0, 200)

def _mae(a, b):
    return float(np.mean(np.abs(np.asarray(a) - np.asarray(b))))

def check(got, exp, case):
    got = np.asarray(got, dtype=float)
    act, train, m = case["actual"], case["train"], case["m"]
    if got.shape != act.shape:
        return False, f"expected an array of length {len(act)}, got shape {got.shape}"
    if not np.all(np.isfinite(got)):
        return False, "forecast contains NaN or inf"
    snaive = np.resize(train[-m:], len(act))
    mae_m, mae_n = _mae(act, got), _mae(act, snaive)
    return mae_m <= 0.9 * mae_n, f"MAE {mae_m:.2f} vs seasonal naive {mae_n:.2f} (need <= 90%: {0.9 * mae_n:.2f})"

CASES = [
    {"name": "weekly season, 7 lags", "call": "hgb_forecast(TR1, 14, 7)", "visible": True, "actual": TE1, "train": TR1, "m": 7},
    {"name": "monthly season, 12 lags", "call": "hgb_forecast(TR2, 12, 12)", "visible": True, "actual": TE2, "train": TR2, "m": 12},
    {"name": "hourly season, 24 lags", "call": "hgb_forecast(TR3, 24, 24)", "actual": TE3, "train": TR3, "m": 24},
    {"name": "more lags than one season", "call": "hgb_forecast(TR1, 14, 14)", "actual": TE1, "train": TR1, "m": 7},
]
