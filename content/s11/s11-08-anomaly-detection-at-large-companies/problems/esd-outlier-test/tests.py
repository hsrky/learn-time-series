import numpy as np

X1 = [10, 11, 9, 10, 10, 11, 9, 10, 100]
rng = np.random.default_rng(3)
XB = rng.normal(50, 5, 500)
XB[[10, 200, 333]] = [95, -10, 120]
XN = rng.normal(0, 1, 300)
X2 = [10, 11, 9, 10, 10, 11, 9, 10, 10, 11, 9, 10, 10, 11, 9, 10, 200, 150]

CASES = [
    {"name": "one clear outlier", "call": "generalized_esd(X1, 2)", "visible": True, "expected": "[8]"},
    {"name": "no outlier in normal data", "call": "generalized_esd(XN, 5)", "visible": True},
    {"name": "two outliers (masking)", "call": "generalized_esd(X2, 3)", "visible": True, "expected": "[16, 17]"},
    {"name": "constant series", "call": "generalized_esd([5, 5, 5, 5, 5], 2)", "expected": "[]"},
    {"name": "three outliers, large sample", "call": "generalized_esd(XB, 10)", "expected": "[10, 200, 333]"},
    {"name": "max_outliers smaller than true count", "call": "generalized_esd(XB, 2)"},
    {"name": "small alpha", "call": "generalized_esd(XB, 10, alpha=0.001)"},
    {"name": "tiny input", "call": "generalized_esd([1.0, 2.0, 30.0], 1)"},
]
