import numpy as np
from numpy.lib.stride_tricks import sliding_window_view


def patchify(x, patch_len, stride, pad=True):
    """Return patches with shape [channels, n_patches, patch_len]."""
    x = np.asarray(x, dtype=float)
    if x.ndim == 1:
        x = x[None, :]                                  # one channel
    C, T = x.shape
    if pad and T > 0:
        x = np.concatenate([x, np.repeat(x[:, -1:], stride, axis=1)], axis=1)
    if x.shape[1] < patch_len:
        return np.empty((C, 0, patch_len))
    # every window of length patch_len, then keep every `stride`-th one
    return sliding_window_view(x, patch_len, axis=1)[:, ::stride].copy()
