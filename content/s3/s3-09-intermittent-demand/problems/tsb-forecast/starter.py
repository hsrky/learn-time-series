import numpy as np


def tsb(y, alpha, beta):
    """TSB forecast per period (probability of demand times demand size)."""
    raise NotImplementedError


def tsb_path(y, alpha, beta):
    """List of forecasts after each period."""
    raise NotImplementedError
