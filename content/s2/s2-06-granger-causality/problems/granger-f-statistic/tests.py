import numpy as np

SY = [0, 1, 0, 2, 1, 3, 2, 4, 3, 5]
SX = [1, 0, 2, 1, 3, 2, 4, 3, 5, 4]

_r = np.random.default_rng(3)
N = 400
X1 = _r.normal(size=N)
Y1 = np.zeros(N)
for _t in range(1, N):
    Y1[_t] = 0.3 * Y1[_t - 1] + 0.8 * X1[_t - 1] + _r.normal(0, 0.5)

_r2 = np.random.default_rng(8)
A = _r2.normal(size=N)
B = _r2.normal(size=N)                      # independent of A
_r3 = np.random.default_rng(9)
U = _r3.normal(size=N)
V = np.zeros(N)
W = np.zeros(N)
for _t in range(1, N):
    V[_t] = 0.6 * U[_t - 1] + _r3.normal(0, 0.5)    # U drives V
    W[_t] = 0.6 * V[_t - 1] + _r3.normal(0, 0.5)    # V drives W

CASES = [
    {"name": "tiny example, p=1", "call": "granger_f(SY, SX, 1)", "visible": True},
    {"name": "x drives y, p=2", "call": "granger_f(Y1, X1, 2)", "visible": True, "tol": 1e-6},
    {"name": "reverse direction is small", "call": "granger_f(X1, Y1, 2)"},
    {"name": "independent series, p=3", "call": "granger_f(A, B, 3)"},
    {"name": "p=5 on random pair", "call": "granger_f(Y1, A, 5)"},
    {"name": "direction x->y", "call": "granger_direction(X1, Y1, 2, 3.0)", "expected": "'x->y'"},
    {"name": "direction y->x", "call": "granger_direction(Y1, X1, 2, 3.0)", "expected": "'y->x'"},
    {"name": "direction none", "call": "granger_direction(A, B, 2, 3.0)", "expected": "'none'"},
    {"name": "chain U->V->W: V and W", "call": "granger_direction(V, W, 1, 3.8)", "expected": "'x->y'"},
]
