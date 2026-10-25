import numpy as np

rng = np.random.default_rng(1)
t = np.arange(280)
WEEKLY = 100 + 8 * np.sin(2 * np.pi * t / 7) + rng.normal(0, 1.5, len(t))
MONTHLY = 50 + 0.8 * t + 6 * np.sin(2 * np.pi * t / 12) + 2 * np.cos(2 * np.pi * 2 * t / 12) + rng.normal(0, 1, len(t))
Q = 30 + 5 * np.sin(2 * np.pi * np.arange(160) / 4) + rng.normal(0, 0.8, 160)
H24 = 200 + 40 * np.sin(2 * np.pi * np.arange(24 * 40) / 24) + rng.normal(0, 4, 24 * 40)
SAW = np.tile([0, 1, 2, 3, 4, 5, 6, 7, 8, 9.0], 20) + rng.normal(0, 0.2, 200)

CASES = [
    {"name": "weekly cycle", "call": "dominant_season(WEEKLY, 10)", "visible": True, "expected": "7"},
    {"name": "trend plus 12-step cycle", "call": "dominant_season(MONTHLY, 20)", "visible": True, "expected": "12"},
    {"name": "quarterly cycle", "call": "dominant_season(Q, 8)", "visible": True, "expected": "4"},
    {"name": "hourly data, daily cycle", "call": "dominant_season(H24, 30)", "expected": "24"},
    {"name": "sawtooth of length 10", "call": "dominant_season(SAW, 15)", "expected": "10"},
    {"name": "returns an int", "call": "type(dominant_season(WEEKLY, 10)).__name__", "expected": "'int'"},
    {"name": "tie goes to the smaller lag (reference value)", "call": "dominant_season(np.tile([1.0, 2.0], 50), 6)"},
]
