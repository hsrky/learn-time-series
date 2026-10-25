import numpy as np

X4 = np.array([1.0, 2.0, 3.0, 4.0])
rng = np.random.default_rng(11)
XB = rng.normal(size=300)
WB = rng.normal(size=5)

CASES = [
    {"name": "sum of two", "call": "causal_conv1d(X4, np.array([1.0, 1.0]))", "visible": True},
    {"name": "dilation 2", "call": "causal_conv1d(X4, np.array([1.0, 1.0]), dilation=2)", "visible": True},
    {"name": "receptive field 16", "call": "receptive_field(2, [1, 2, 4, 8])", "visible": True},
    {"name": "uses past only (impulse)", "call": "causal_conv1d(np.array([1.0, 0, 0, 0, 0]), np.array([1.0, 2.0, 3.0]))"},
    {"name": "dilation larger than series", "call": "causal_conv1d(X4, np.array([1.0, 5.0]), dilation=10)"},
    {"name": "empty input", "call": "causal_conv1d(np.array([]), np.array([1.0, 2.0]))"},
    {"name": "random long", "call": "causal_conv1d(XB, WB, dilation=3)"},
    {"name": "receptive field k=3", "call": "receptive_field(3, [1, 2, 4])"},
    {"name": "receptive field single layer", "call": "receptive_field(5, [1])"},
]
