def choose_option(options, volume, max_latency_ms):
    """Cheapest option that meets the latency limit.
    Return {"best": name or None, "cost": float or None, "ranking": [names]}."""
    raise NotImplementedError


def breakeven_volume(a, b):
    """Monthly volume where options a and b cost the same, or None."""
    raise NotImplementedError
