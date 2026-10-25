import numpy as np

rng = np.random.default_rng(17)
N = 600
T = np.arange(N)
SD = np.where(T < 300, 1.0, 3.0)
BY = 50 + 5 * np.sin(2 * np.pi * T / 7) + rng.normal(0, 1, N) * SD
BH = np.full(N, np.nan)
BH[7:] = BY[:-7]
Y1 = [10.0, 12.0, 11.0, 14.0, 13.0]
H1 = [9.0, 13.0, 11.0, 12.0, 13.0]

CASES = [
    {"name": "small example", "call": "rolling_conformal(Y1, H1, 0.5, 3)", "visible": True,
     "expected": "(np.array([np.nan, 12.0, 10.0, 11.0, 12.0]), np.array([np.nan, 14.0, 12.0, 13.0, 14.0]))"},
    {"name": "interval at t never uses y[t]", "call": "rolling_conformal([0, 0, 1000.0], [0, 0, 0.0], 0.5, 5)", "visible": True,
     "expected": "(np.array([np.nan, 0.0, 0.0]), np.array([np.nan, 0.0, 0.0]))"},
    {"name": "too few residuals gives inf", "call": "rolling_conformal([1, 2, 3.0], [1, 1, 1.0], 0.1, 5)", "visible": True,
     "expected": "(np.array([np.nan, -np.inf, -np.inf]), np.array([np.nan, np.inf, np.inf]))"},
    {"name": "window of 1", "call": "rolling_conformal(Y1, H1, 0.5, 1)"},
    {"name": "nan forecasts are skipped", "call": "rolling_conformal([1, 2, 3, 4, 5.0], [np.nan, np.nan, 3, 3, 3.0], 0.5, 4)"},
    {"name": "single point", "call": "rolling_conformal([5.0], [4.0], 0.2, 10)",
     "expected": "(np.array([np.nan]), np.array([np.nan]))"},
    {"name": "seasonal naive on noisy data, window 60", "call": "rolling_conformal(BY, BH, 0.2, 60)"},
    {"name": "seasonal naive, window 200", "call": "rolling_conformal(BY, BH, 0.1, 200)"},
]
