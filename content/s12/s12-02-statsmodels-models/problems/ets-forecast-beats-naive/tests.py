import numpy as np

def make(seed, n, h, m, slope, amp, sd, level=100.0):
    rng = np.random.default_rng(seed)
    t = np.arange(n + h)
    y = level + slope * t + amp * np.sin(2 * np.pi * t / m) + 0.5 * amp * np.cos(2 * np.pi * 2 * t / m) + rng.normal(0, sd, n + h)
    return y[:n], y[n:]

TR1, TE1 = make(1, 70, 14, 7, 1.2, 10, 2.0)
TR2, TE2 = make(2, 96, 12, 12, 0.8, 8, 1.5, level=60)
TR3, TE3 = make(3, 168, 24, 24, 0.3, 20, 3.0, level=300)
TR4, TE4 = make(4, 56, 7, 7, 2.0, 5, 1.0, level=20)

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
    ok = mae_m <= 0.8 * mae_n
    return ok, f"MAE {mae_m:.2f} vs seasonal naive {mae_n:.2f} (need <= 80%: {0.8 * mae_n:.2f})"

CASES = [
    {"name": "daily data, weekly season", "call": "ets_forecast(TR1, 14, 7)", "visible": True, "actual": TE1, "train": TR1, "m": 7},
    {"name": "monthly data", "call": "ets_forecast(TR2, 12, 12)", "visible": True, "actual": TE2, "train": TR2, "m": 12},
    {"name": "hourly data, daily season", "call": "ets_forecast(TR3, 24, 24)", "visible": True, "actual": TE3, "train": TR3, "m": 24},
    {"name": "short history, strong trend", "call": "ets_forecast(TR4, 7, 7)", "actual": TE4, "train": TR4, "m": 7},
]
