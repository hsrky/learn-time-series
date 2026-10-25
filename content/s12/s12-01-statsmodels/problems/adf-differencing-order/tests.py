import numpy as np

rng = np.random.default_rng(42)
NOISE = rng.normal(0, 1, 300)
WALK = np.cumsum(rng.normal(0, 1, 300))
DOUBLE = np.cumsum(np.cumsum(rng.normal(0, 1, 300)))
TREND_STAT = 0.05 * np.arange(300) + rng.normal(0, 1, 300)
SEAS = 10 * np.sin(2 * np.pi * np.arange(400) / 12) + rng.normal(0, 1, 400)

CASES = [
    {"name": "white noise", "call": "differencing_order(NOISE)", "visible": True, "expected": "0"},
    {"name": "random walk", "call": "differencing_order(WALK)", "visible": True, "expected": "1"},
    {"name": "twice integrated series", "call": "differencing_order(DOUBLE)", "visible": True, "expected": "2"},
    {"name": "max_d limits the answer", "call": "differencing_order(DOUBLE, max_d=1)", "expected": "1"},
    {"name": "constant series", "call": "differencing_order(np.ones(50))", "expected": "0"},
    {"name": "very short series", "call": "differencing_order([1.0, 2.0, 3.0])", "expected": "0"},
    {"name": "stationary seasonal series", "call": "differencing_order(SEAS)"},
    {"name": "strict alpha on a trend", "call": "differencing_order(TREND_STAT, alpha=0.001)"},
]
