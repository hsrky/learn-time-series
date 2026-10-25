import numpy as np
import pandas as pd

D1 = pd.DataFrame({"group": ["A", "A", "A"],
                   "date": pd.to_datetime(["2024-01-01", "2024-01-03", "2024-01-08"]),
                   "actual": [100.0, 100.0, 50.0], "forecast": [90.0, 120.0, 50.0]})
D2 = pd.DataFrame({"group": ["B", "A", "B", "A"],
                   "date": pd.to_datetime(["2024-01-07 23:00", "2024-01-07 01:00", "2024-01-08 09:30", "2024-01-06 00:00"]),
                   "actual": [10.0, 0.0, 20.0, 0.0], "forecast": [5.0, 3.0, 20.0, 1.0]})
D3 = pd.DataFrame({"group": [], "date": pd.to_datetime([]), "actual": [], "forecast": []})
rng = np.random.default_rng(21)
days = pd.date_range("2024-01-01", periods=70, freq="D")
rows = [(g, d, float(rng.integers(0, 40)), float(rng.integers(0, 40))) for g in "XYZ" for d in days]
D4 = pd.DataFrame(rows, columns=["group", "date", "actual", "forecast"]).sample(frac=1, random_state=2)

CASES = [
    {"name": "example", "call": "weekly_wape(D1)", "visible": True,
     "expected": "pd.DataFrame({'group': ['A','A'], 'week_start': pd.to_datetime(['2024-01-01','2024-01-08']), 'wape': [0.15, 0.0]})"},
    {"name": "Sunday belongs to the previous week; zero actuals", "call": "weekly_wape(D2)", "visible": True,
     "expected": "pd.DataFrame({'group': ['A','B','B'], 'week_start': pd.to_datetime(['2024-01-01','2024-01-01','2024-01-08']), 'wape': [np.nan, 0.5, 0.0]})"},
    {"name": "empty", "call": "weekly_wape(D3)", "check_index": False},
    {"name": "larger random", "call": "weekly_wape(D4)"},
]
