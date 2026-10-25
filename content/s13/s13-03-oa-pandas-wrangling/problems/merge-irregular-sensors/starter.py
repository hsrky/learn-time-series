import pandas as pd


def attach_latest(a, b, tol_seconds):
    """For each row of a, attach the latest humidity of the same device that is not in the future
    and not older than tol_seconds. Return device, time, temp, humidity sorted by device, time."""
    raise NotImplementedError
