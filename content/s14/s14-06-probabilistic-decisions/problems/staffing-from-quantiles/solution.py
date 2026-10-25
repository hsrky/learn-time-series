import math


def _demand_at(q, p):
    levels = sorted(q)
    if p <= levels[0]:
        return float(q[levels[0]])              # below the lowest level
    if p >= levels[-1]:
        return float(q[levels[-1]])             # above the highest level
    for lo, hi in zip(levels, levels[1:]):
        if lo <= p <= hi:
            w = (p - lo) / (hi - lo)            # linear interpolation weight
            return q[lo] + (q[hi] - q[lo]) * w


def staff_levels(intervals, capacity, service_level, min_staff=1, max_staff=None):
    """Staff needed per interval to cover demand at the given service level."""
    out = []
    for q in intervals:
        d = _demand_at(q, service_level)
        s = max(min_staff, math.ceil(round(d / capacity, 9)))   # always round up
        if max_staff is not None:
            s = min(s, max_staff)
        out.append(int(s))
    return out
