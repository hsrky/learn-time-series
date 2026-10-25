def sessionize(events):
    out = []                                        # [user, start, end, count]
    for user, ts in sorted(events):
        if out and out[-1][0] == user and ts - out[-1][2] <= 1800:
            out[-1][2] = ts
            out[-1][3] += 1
        else:
            out.append([user, ts, ts, 1])
    return [tuple(s) for s in out]
