import numpy as np

G1 = np.array([1.0]); B1 = np.array([0.0])
X1 = np.array([[[1.0], [2.0], [3.0]]])
rng = np.random.default_rng(4)
XB = rng.normal(size=(8, 96, 3)) * np.array([1.0, 50.0, 0.01]) + np.array([0.0, 1000.0, 5.0])
GB = np.array([1.5, 0.5, 2.0]); BB = np.array([0.1, -0.2, 0.0])
YB = rng.normal(size=(8, 24, 3))
XN, MN, SD = None, None, None

CASES = [
    {"name": "1 2 3", "call": "revin_normalize(X1, G1, B1)", "visible": True},
    {"name": "round trip", "call": "revin_denormalize(revin_normalize(X1, G1, B1)[0], *revin_normalize(X1, G1, B1)[1:], G1, B1)", "visible": True},
    {"name": "denormalize a forecast", "call": "revin_denormalize(np.array([[[0.0],[1.0]]]), np.array([[[10.0]]]), np.array([[[2.0]]]), G1, B1)", "visible": True},
    {"name": "constant window uses eps", "call": "revin_normalize(np.full((1, 4, 1), 7.0), G1, B1)"},
    {"name": "empty batch", "call": "revin_normalize(np.zeros((0, 5, 2)), np.ones(2), np.zeros(2))"},
    {"name": "3 channels, very different scales", "call": "revin_normalize(XB, GB, BB)"},
    {"name": "round trip random", "call": "(lambda r: revin_denormalize(r[0], r[1], r[2], GB, BB))(revin_normalize(XB, GB, BB))"},
    {"name": "denormalize random forecast", "call": "(lambda r: revin_denormalize(YB, r[1], r[2], GB, BB))(revin_normalize(XB, GB, BB))"},
]
