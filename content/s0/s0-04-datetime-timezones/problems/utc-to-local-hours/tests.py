import numpy as np
import pandas as pd

rng = np.random.default_rng(4)
base = pd.Timestamp("2024-01-01")
BIG = [str(base + pd.Timedelta(minutes=int(m))) for m in rng.integers(0, 60 * 24 * 365, 3000)]

CASES = [
    {"name": "july New York", "call": "local_hours(['2024-07-01 03:10', '2024-07-01 14:05'], 'America/New_York')", "expected": "[23, 10]", "visible": True},
    {"name": "tokyo", "call": "local_hours(['2024-01-01 12:00'], 'Asia/Tokyo')", "expected": "[21]", "visible": True},
    {"name": "winter vs summer", "call": "local_hours(['2024-01-15 12:00', '2024-07-15 12:00'], 'Europe/Berlin')", "expected": "[13, 14]"},
    {"name": "spring forward gap", "call": "local_hours(['2024-03-10 06:59', '2024-03-10 07:00'], 'America/New_York')", "expected": "[1, 3]"},
    {"name": "fall back repeats 1am", "call": "local_hours(['2024-11-03 05:30', '2024-11-03 06:30'], 'America/New_York')", "expected": "[1, 1]"},
    {"name": "half-hour zone", "call": "local_hours(['2024-06-01 00:00'], 'Asia/Kolkata')", "expected": "[5]"},
    {"name": "empty", "call": "local_hours([], 'UTC')", "expected": "[]"},
    {"name": "random 3000", "call": "local_hours(BIG, 'America/Chicago')"},
]
