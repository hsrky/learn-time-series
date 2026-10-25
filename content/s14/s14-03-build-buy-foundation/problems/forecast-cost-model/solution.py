def _cost(o, volume):
    return float(o["fixed"]) + float(o["per_1k"]) * volume / 1000.0


def choose_option(options, volume, max_latency_ms):
    """Cheapest option that meets the latency limit.
    Return {"best": name or None, "cost": float or None, "ranking": [names]}."""
    ok = [o for o in options if o["latency_ms"] <= max_latency_ms]     # hard limit first
    ranked = sorted(((_cost(o, volume), o["name"]) for o in ok))        # cost, then name
    if not ranked:
        return {"best": None, "cost": None, "ranking": []}
    return {"best": ranked[0][1], "cost": ranked[0][0], "ranking": [n for _, n in ranked]}


def breakeven_volume(a, b):
    """Monthly volume where options a and b cost the same, or None."""
    dp = float(a["per_1k"]) - float(b["per_1k"])
    if dp == 0:
        return None
    v = (float(b["fixed"]) - float(a["fixed"])) * 1000.0 / dp
    return v if v > 0 else None
