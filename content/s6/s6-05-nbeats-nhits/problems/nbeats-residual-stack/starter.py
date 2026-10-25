import numpy as np


def nbeats_forward(x, blocks):
    """x: [batch, L]; blocks: list of (Wb [L, L], Wf [L, H]). Return (forecast_sum, residual)."""
    raise NotImplementedError
