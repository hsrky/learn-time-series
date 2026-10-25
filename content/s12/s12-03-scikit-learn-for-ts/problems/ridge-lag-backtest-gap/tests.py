import numpy as np

LINE = np.arange(1, 41, dtype=float)
rng = np.random.default_rng(6)
t = np.arange(300)
AR = np.zeros(300)
for i in range(1, 300):
    AR[i] = 0.7 * AR[i - 1] + rng.normal()
SEAS = 50 + 0.2 * t + 8 * np.sin(2 * np.pi * t / 7) + rng.normal(0, 2, 300)

CASES = [
    {"name": "perfect line", "call": "backtest_mae(LINE, 2, 3, 0)", "visible": True, "expected": "0.0", "tol": 1e-6},
    {"name": "AR(1) series, 2 lags", "call": "backtest_mae(AR, 2, 4, 0)", "visible": True},
    {"name": "gap of 5 rows", "call": "backtest_mae(AR, 2, 4, 5)", "visible": True},
    {"name": "weekly season, 7 lags", "call": "backtest_mae(SEAS, 7, 5, 0)"},
    {"name": "weekly season, gap 7", "call": "backtest_mae(SEAS, 7, 5, 7)"},
    {"name": "one lag, two splits", "call": "backtest_mae(SEAS[:60], 1, 2, 0)"},
]
