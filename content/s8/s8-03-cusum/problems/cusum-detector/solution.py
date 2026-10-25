def cusum_detect(values, mu, k, h):
    s_up = s_dn = 0.0
    out = []
    for t, x in enumerate(values):
        s_up = max(0.0, s_up + x - mu - k)
        s_dn = max(0.0, s_dn + mu - x - k)
        if s_up > h:
            out.append((t, "up"))
            s_up = s_dn = 0.0
        elif s_dn > h:
            out.append((t, "down"))
            s_up = s_dn = 0.0
    return out
