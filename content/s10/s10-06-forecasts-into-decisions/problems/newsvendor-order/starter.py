import math
import numpy as np


def expected_cost(q, samples, cu, co):
    """Average of cu * max(d - q, 0) + co * max(q - d, 0) over the samples d."""
    raise NotImplementedError


def newsvendor_order(samples, cu, co):
    """The k-th smallest sample, k = max(1, ceil(cu / (cu + co) * n - 1e-9))."""
    raise NotImplementedError
