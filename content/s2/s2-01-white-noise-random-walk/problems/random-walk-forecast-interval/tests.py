CASES = [
    {"name": "flat forecast", "call": "random_walk_forecast(100, 3, 2.0)", "visible": True},
    {"name": "with drift", "call": "random_walk_forecast(10, 2, 1.0, drift=0.5)", "visible": True},
    {"name": "h = 1", "call": "random_walk_forecast(5.0, 1, 3.0)"},
    {"name": "sigma zero", "call": "random_walk_forecast(7, 4, 0.0, drift=-1.0)"},
    {"name": "custom z", "call": "random_walk_forecast(0, 5, 1.5, z=1.645)"},
    {"name": "negative drift, long", "call": "random_walk_forecast(-20.5, 100, 0.7, drift=-0.1)"},
]
