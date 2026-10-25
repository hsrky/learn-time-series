import numpy as np
import pandas as pd


def hierarchy_weights(bottom, levels):
    """Revenue-share weights for each group of each level. Columns: level, key, weight."""
    raise NotImplementedError


def rmsse(train, actual, forecast):
    """Root mean squared scaled error; the scale starts at the first non-zero training value."""
    raise NotImplementedError
