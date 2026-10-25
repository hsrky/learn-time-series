import numpy as np

W1 = np.array([[0.5]]); U1 = np.array([[0.9]]); B1 = np.array([0.0])
rng = np.random.default_rng(3)
Wx = rng.normal(size=(3, 4)) * 0.5
Wh = rng.normal(size=(4, 4)) * 0.5
Bb = rng.normal(size=4) * 0.1
XS = rng.normal(size=(20, 3))

CASES = [
    {"name": "single step", "call": "rnn_step(np.array([1.0]), np.array([0.0]), W1, U1, B1)", "visible": True},
    {"name": "two steps", "call": "rnn_forward(np.array([[1.0],[1.0]]), W1, U1, B1)", "visible": True},
    {"name": "step with memory", "call": "rnn_step(np.array([0.2,-1.0,0.5]), np.array([0.1,0.2,-0.3,0.4]), Wx, Wh, Bb)", "visible": True},
    {"name": "zero input keeps decaying", "call": "rnn_forward(np.zeros((5, 1)), W1, U1, np.array([0.3]))"},
    {"name": "empty sequence", "call": "rnn_forward(np.zeros((0, 3)), Wx, Wh, Bb)"},
    {"name": "random 20 steps", "call": "rnn_forward(XS, Wx, Wh, Bb)"},
    {"name": "big input saturates", "call": "rnn_forward(np.full((3, 1), 100.0), W1, U1, B1)"},
]
