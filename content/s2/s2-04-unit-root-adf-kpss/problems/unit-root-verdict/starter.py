import warnings

import numpy as np
from statsmodels.tsa.stattools import adfuller, kpss


def unit_root_verdict(x, alpha=0.05):
    """Return {"adf_p": float, "kpss_p": float, "verdict": str}."""
    raise NotImplementedError


def suggest_d(x, max_d=2, alpha=0.05):
    """Smallest d in 0..max_d giving a 'stationary' verdict after d first differences."""
    raise NotImplementedError
