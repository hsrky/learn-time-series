def longest_calm_stretch(values, tol):
    """Length of the longest run of days whose day-to-day change is at most tol."""
    if len(values) == 0:
        return 0
    best = run = 1
    for i in range(1, len(values)):
        if abs(values[i] - values[i - 1]) <= tol:
            run += 1                # still calm: extend the run
        else:
            run = 1                 # a jump: start again
        best = max(best, run)
    return best
