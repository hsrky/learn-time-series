import numpy as np
import pandas as pd


def rmspe(y_true, y_pred):
    """RMSPE over rows with y_true != 0 (0.0 if there are none)."""
    raise NotImplementedError


def apply_open_rule(df):
    """0.0 where Open == 0, else pred. A missing Open counts as open."""
    raise NotImplementedError
