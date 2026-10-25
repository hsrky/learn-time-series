import numpy as np


def tokenize(x, n_bins=16, low=-4.0, high=4.0):
    """Return (tokens, scale). Token 0 = PAD (NaN), bins use ids 2 .. n_bins+1."""
    x = np.asarray(x, dtype=float)
    valid = ~np.isnan(x)
    # 1) mean scaling: the typical size of the values in the context
    scale = float(np.abs(x[valid]).mean()) if valid.any() else 1.0
    if scale == 0.0:
        scale = 1.0
    scaled = x / scale
    # 2) uniform quantization into n_bins bins between low and high
    width = (high - low) / n_bins
    safe = np.where(valid, scaled, 0.0)
    b = np.clip(np.floor((safe - low) / width), 0, n_bins - 1).astype(int)
    tokens = b + 2                       # shift: 0 = PAD, 1 = EOS
    tokens[~valid] = 0                   # missing values -> PAD
    return tokens, scale


def detokenize(tokens, scale, n_bins=16, low=-4.0, high=4.0):
    """Bin centers times scale; PAD becomes NaN."""
    tokens = np.asarray(tokens)
    width = (high - low) / n_bins
    centers = low + (tokens - 2 + 0.5) * width
    out = centers * scale
    out = np.where(tokens < 2, np.nan, out)
    return out
