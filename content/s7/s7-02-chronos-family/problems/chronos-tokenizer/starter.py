import numpy as np


def tokenize(x, n_bins=16, low=-4.0, high=4.0):
    """Return (tokens, scale). Token 0 = PAD (NaN), bins use ids 2 .. n_bins+1."""
    raise NotImplementedError


def detokenize(tokens, scale, n_bins=16, low=-4.0, high=4.0):
    """Bin centers times scale; PAD becomes NaN."""
    raise NotImplementedError
