import numpy as np


def owa(train, test, fc, fc_naive2, m):
    """M4 OWA of `fc` against `fc_naive2`.

    train, test, fc, fc_naive2: lists of 1-D arrays (one per series). m: season length.
    sMAPE = mean(200*|y-f|/(|y|+|f|)); MASE = mean|y-f| / mean|train[t]-train[t-m]|.
    OWA = 0.5*(sMAPE/sMAPE_naive2 + MASE/MASE_naive2), with sMAPE and MASE averaged over series.
    """
    raise NotImplementedError
