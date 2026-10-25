import numpy as np


def pinball_loss(y_true, y_pred, tau):
    """Mean pinball loss of the quantile forecast y_pred at level tau."""
    # Your code here
    raise NotImplementedError


def weighted_quantile_loss(y_true, preds, taus):
    """2 * summed pinball loss / (number of levels * sum |y_true|)."""
    # Your code here
    raise NotImplementedError
