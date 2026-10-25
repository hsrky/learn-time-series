import numpy as np


def nbeats_forward(x, blocks):
    """x: [batch, L]; blocks: list of (Wb [L, L], Wf [L, H]). Return (forecast_sum, residual)."""
    r = np.asarray(x, dtype=float)
    total = None
    for Wb, Wf in blocks:
        backcast = r @ Wb              # what this block explains of the past
        forecast = r @ Wf              # its contribution to the future
        r = r - backcast               # the next block sees only what is left
        total = forecast if total is None else total + forecast
    return total, r
