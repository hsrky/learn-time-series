CASES = [
    {"name": "AR(1) signature", "call": "suggest_orders([1, 0.7, 0.5, 0.3, 0.1], [1, 0.7, 0.05, 0.02, 0.0], 100)", "visible": True},
    {"name": "white noise", "call": "suggest_orders([1, 0.1, 0.05], [1, 0.1, 0.05], 100)", "visible": True},
    {"name": "MA(2) signature", "call": "suggest_orders([1, 0.5, 0.3, 0.05, 0.02], [1, 0.4, 0.25, 0.2, 0.15], 100)"},
    {"name": "only PACF significant", "call": "suggest_orders([1, 0.1, 0.1], [1, 0.1, 0.5], 100)"},
    {"name": "only ACF significant", "call": "suggest_orders([1, 0.1, 0.5], [1, 0.1, 0.1], 100)"},
    {"name": "equal cut-offs give ARMA", "call": "suggest_orders([1, 0.6, 0.4, 0.01], [1, 0.6, 0.4, 0.01], 100)"},
    {"name": "value equal to the band is not significant", "call": "suggest_orders([1, 0.196, 0.0], [1, 0.0, 0.0], 100)"},
    {"name": "negative values count", "call": "suggest_orders([1, -0.6, 0.05], [1, -0.6, -0.4], 100)"},
]
