CASES = [
    {"name": "MA(1) theta 0.5", "call": "ma_invertible([0.5])", "visible": True},
    {"name": "MA(1) theta 2", "call": "ma_invertible([2.0])", "visible": True},
    {"name": "AR(2) stationary", "call": "ar_stationary([0.6, 0.3])", "visible": True},
    {"name": "empty list", "call": "(ma_invertible([]), ar_stationary([]))", "expected": "(True, True)"},
    {"name": "MA(1) negative theta", "call": "ma_invertible([-0.9])"},
    {"name": "MA(1) theta exactly 1 is not invertible", "call": "ma_invertible([1.0])"},
    {"name": "MA(2) invertible", "call": "ma_invertible([0.4, 0.3])"},
    {"name": "MA(2) close to the boundary", "call": "ma_invertible([0.5, 0.9])"},
    {"name": "AR(1) phi 1 is a random walk", "call": "ar_stationary([1.0])"},
    {"name": "AR(2) with big coefficients", "call": "ar_stationary([0.5, 0.6])"},
    {"name": "trailing zero is ignored", "call": "ma_invertible([0.5, 0.0])"},
]
