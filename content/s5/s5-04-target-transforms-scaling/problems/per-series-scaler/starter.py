import numpy as np
import pandas as pd


class PerSeriesScaler:
    def __init__(self, log=True):
        self.log = log
        self.mu = {}
        self.sd = {}

    def fit(self, df, cutoff):
        """Learn mu and sd per series from rows with date < cutoff."""
        # Your code here
        raise NotImplementedError

    def transform(self, df):
        """Return a Series of scaled values aligned with df."""
        # Your code here
        raise NotImplementedError

    def inverse_transform(self, series_ids, z):
        """Return values in original units as a numpy array."""
        # Your code here
        raise NotImplementedError
