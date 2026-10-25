import numpy as np


def route(val_err, test_err):
    """Pick a model per series by validation error; compare with the global best model."""
    val_err = np.asarray(val_err, dtype=float)
    test_err = np.asarray(test_err, dtype=float)
    M, S = val_err.shape
    if S == 0:
        return {"choice": [], "global": 0, "router_test": 0.0, "global_test": 0.0}
    choice = np.argmin(val_err, axis=0)                 # best model per series (first on ties)
    glob = int(np.argmin(val_err.mean(axis=1)))         # one model for everybody
    router_test = test_err[choice, np.arange(S)].mean() # errors of the chosen models
    global_test = test_err[glob].mean()
    return {"choice": [int(c) for c in choice], "global": glob,
            "router_test": float(router_test), "global_test": float(global_test)}
