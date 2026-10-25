def mean_valid(readings):
    """Return the mean of the readings that are not None (nan if there are none)."""
    # Keep only real values. "is not None" keeps 0 and 0.0, which are valid readings.
    valid = [r for r in readings if r is not None]
    if not valid:
        return float("nan")
    return sum(valid) / len(valid)
