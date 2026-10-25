import numpy as np


def make(seed, n=300, h=14):
    rng = np.random.default_rng(100 + seed)
    t = np.arange(n + h)
    y = (40 + rng.uniform(0.1, 0.3) * t + rng.uniform(4, 10) * np.sin(2 * np.pi * t / 7 + rng.uniform(0, 6))
         + rng.normal(0, 1.5, n + h))
    return y[:n], y[n:]


def snaive(train, h):
    return np.array([train[-7 + (i % 7)] for i in range(h)])


DATA = {s: make(s) for s in range(3)}
SHORT = make(7, n=80, h=7)
DOWN_TRAIN = 200 - 0.3 * np.arange(250) + 5 * np.sin(2 * np.pi * np.arange(250) / 7) + np.random.default_rng(9).normal(0, 1.2, 250)

CASES = [
    {"name": "trend up, seed 0", "call": "forecast(DATA[0][0], 14)", "visible": True, "truth": "DATA[0][1]"},
    {"name": "trend up, seed 1", "call": "forecast(DATA[1][0], 14)", "visible": True, "truth": "DATA[1][1]"},
    {"name": "trend up, seed 2", "call": "forecast(DATA[2][0], 14)", "truth": "DATA[2][1]"},
    {"name": "short history, horizon 7", "call": "forecast(SHORT[0], 7)", "truth": "SHORT[1]"},
    {"name": "trend down", "call": "forecast(DOWN_TRAIN[:236], 14)", "truth": "DOWN_TRAIN[236:250]"},
]


def check(got, exp, case):
    truth = np.asarray(eval(case["truth"]), dtype=float)
    got = np.asarray(got, dtype=float)
    if got.shape != truth.shape:
        return False, f"expected {len(truth)} values, got shape {got.shape}"
    if not np.all(np.isfinite(got)):
        return False, "forecast contains NaN or inf"
    train = eval(case["call"].split("(")[1].split(",")[0])
    base = snaive(np.asarray(train, dtype=float), len(truth))
    mae, mae_base = np.abs(got - truth).mean(), np.abs(base - truth).mean()
    ok = mae <= 0.9 * mae_base
    return ok, f"MAE {mae:.2f} vs seasonal naive {mae_base:.2f} (need <= {0.9 * mae_base:.2f})"
