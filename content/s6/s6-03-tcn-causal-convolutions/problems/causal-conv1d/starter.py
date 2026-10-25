import numpy as np


def causal_conv1d(x, w, dilation=1):
    """y[t] = sum_j w[j] * x[t - j*dilation]; missing past values are 0."""
    raise NotImplementedError


def receptive_field(kernel_size, dilations):
    """Number of time steps seen by the last layer of a stack."""
    raise NotImplementedError
