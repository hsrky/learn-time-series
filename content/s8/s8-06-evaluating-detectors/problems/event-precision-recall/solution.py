def event_precision_recall(true_events, pred_events):
    T = sorted(true_events)
    P = sorted(pred_events)
    t_hit = [False] * len(T)
    p_hit = [False] * len(P)
    i = j = 0
    while i < len(T) and j < len(P):
        a, b = T[i], P[j]
        if a[0] <= b[1] and b[0] <= a[1]:       # overlap
            t_hit[i] = True
            p_hit[j] = True
        if a[1] < b[1]:                         # the interval that ends first cannot match later ones
            i += 1
        else:
            j += 1
    prec = sum(p_hit) / len(P) if P else 0.0
    rec = sum(t_hit) / len(T) if T else 0.0
    f1 = 0.0 if prec + rec == 0 else 2 * prec * rec / (prec + rec)
    return {"precision": float(prec), "recall": float(rec), "f1": float(f1)}
