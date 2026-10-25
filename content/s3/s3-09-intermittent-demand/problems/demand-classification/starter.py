import numpy as np
import pandas as pd


def classify_demand(y):
    """Return {"adi": float, "cv2": float, "class": str}."""
    raise NotImplementedError


def classify_table(df):
    """DataFrame (columns = items) -> DataFrame (index = items; columns adi, cv2, class)."""
    raise NotImplementedError
