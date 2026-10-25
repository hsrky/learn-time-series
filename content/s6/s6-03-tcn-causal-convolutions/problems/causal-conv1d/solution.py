import numpy as np


def causal_conv1d(x, w, dilation=1):
    """y[t] = sum_j w[j] * x[t - j*dilation]; missing past values are 0."""
    x = np.asarray(x, dtype=float)
    n = len(x)
    y = np.zeros(n)
    for j, wj in enumerate(w):
        shift = j * dilation
        if shift >= n:
            break                        # this tap only sees the zero padding
        y[shift:] += wj * x[:n - shift]  # x delayed by `shift` steps: past only
    return y


def receptive_field(kernel_size, dilations):
    """Number of time steps seen by the last layer of a stack."""
    return 1 + (kernel_size - 1) * sum(dilations)
