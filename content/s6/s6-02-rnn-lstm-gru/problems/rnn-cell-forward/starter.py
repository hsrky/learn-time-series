import numpy as np


def rnn_step(x, h, Wxh, Whh, b):
    """New hidden state, shape [H]."""
    raise NotImplementedError


def rnn_forward(X, Wxh, Whh, b):
    """All hidden states, shape [T, H], starting from h = 0."""
    raise NotImplementedError
