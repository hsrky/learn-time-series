import numpy as np
import pandas as pd

d14 = pd.date_range("2024-01-01", periods=14)
TR1 = pd.DataFrame({"store_nbr": 1, "family": "A", "date": d14, "sales": np.arange(1.0, 15.0)})
TD1 = pd.to_datetime(["2024-01-15", "2024-01-22"])

TR2 = pd.concat([TR1, pd.DataFrame({"store_nbr": 2, "family": "B", "date": d14, "sales": np.arange(14.0, 0, -1)})])
TR2 = TR2[~((TR2["store_nbr"] == 2) & (TR2["date"] == "2024-01-12"))]          # a missing day in series 2
TD2 = pd.date_range("2024-01-15", periods=4)

rng = np.random.default_rng(6)
dd = pd.date_range("2024-01-01", periods=60)
rows = [pd.DataFrame({"store_nbr": s, "family": f, "date": dd, "sales": np.round(rng.uniform(0, 100, 60), 2)})
        for s in (3, 1, 2) for f in ("Z", "Y")]
TR3 = pd.concat(rows).sample(frac=1.0, random_state=1)
TD3 = pd.date_range("2024-03-01", periods=16)                                # 16 days: more than 2 seasons
YT = list(rng.uniform(0, 500, 200)); YP = list(rng.uniform(-5, 500, 200))

CASES = [
    {"name": "rmsle zero error", "call": "rmsle([3, 0], [3, 0])", "expected": "0.0", "visible": True},
    {"name": "rmsle one big miss", "call": "rmsle([0], [3])", "expected": "math.log(4)", "visible": True},
    {"name": "seasonal naive, one series", "call": "seasonal_naive_forecast(TR1, TD1)", "visible": True,
     "expected": "pd.DataFrame({'store_nbr': [1, 1], 'family': ['A', 'A'], 'date': TD1, 'sales': [8.0, 8.0]})"},
    {"name": "rmsle clips negative predictions", "call": "rmsle([1, 2], [-4, 2])", "expected": "math.sqrt((math.log(2) ** 2) / 2)"},
    {"name": "missing source day gives 0", "call": "seasonal_naive_forecast(TR2, TD2)"},
    {"name": "16-day horizon, shuffled rows", "call": "seasonal_naive_forecast(TR3, TD3)"},
    {"name": "rmsle random", "call": "rmsle(YT, YP)"},
]
