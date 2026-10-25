import numpy as np

_t = np.arange(70)
EXACT = 100 + 0.5 * _t + 10 * np.sin(2 * np.pi * _t / 7)
_r = np.random.default_rng(9)
_t2 = np.arange(300)
NOISY = 50 + 0.05 * _t2 + 8 * np.sin(2 * np.pi * _t2 / 12) + 3 * np.cos(4 * np.pi * _t2 / 12) + _r.normal(0, 1, 300)
FUTURE = lambda t: 100 + 0.5 * t + 10 * np.sin(2 * np.pi * t / 7)

CASES = [
    {"name": "straight line, K = 0", "call": "trend_fourier_forecast([10, 12, 14, 16, 18], 4, 0, 2)", "visible": True},
    {"name": "exact weekly sine", "call": "trend_fourier_forecast(EXACT, 7, 1, 7)", "expected": "FUTURE(np.arange(70, 77))", "tol": 1e-6, "visible": True},
    {"name": "h = 0", "call": "trend_fourier_forecast(EXACT, 7, 1, 0)", "expected": "np.array([])"},
    {"name": "noisy monthly data, K = 2", "call": "trend_fourier_forecast(NOISY[:288], 12, 2, 12)", "tol": 1e-6},
    {"name": "K too small leaves error", "call": "float(np.mean(np.abs(trend_fourier_forecast(NOISY[:288], 12, 1, 12) - NOISY[288:]))) > float(np.mean(np.abs(trend_fourier_forecast(NOISY[:288], 12, 2, 12) - NOISY[288:])))", "expected": "True"},
    {"name": "beats seasonal naive", "call": "float(np.mean(np.abs(trend_fourier_forecast(NOISY[:288], 12, 2, 12) - NOISY[288:]))) < float(np.mean(np.abs(NOISY[276:288] - NOISY[288:])))", "expected": "True"},
    {"name": "period not an integer", "call": "trend_fourier_forecast(NOISY[:200], 29.5, 2, 5)", "tol": 1e-6},
]
