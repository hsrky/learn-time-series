import numpy as np


def rnn_step(x, h, Wxh, Whh, b):
    """New hidden state, shape [H]."""
    # mix the new input with the old memory, then squash to (-1, 1)
    return np.tanh(x @ Wxh + h @ Whh + b)


def rnn_forward(X, Wxh, Whh, b):
    """All hidden states, shape [T, H], starting from h = 0."""
    H = Whh.shape[0]
    h = np.zeros(H)
    states = []
    for x in X:                      # time must go in order: step t needs step t-1
        h = rnn_step(x, h, Wxh, Whh, b)
        states.append(h)
    return np.array(states).reshape(len(states), H)
