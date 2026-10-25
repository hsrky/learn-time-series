import math


def rank_models(models, n, criterion="aic"):
    if criterion not in ("aic", "bic"):
        raise ValueError("criterion must be 'aic' or 'bic'")
    penalty = (lambda k: 2 * k) if criterion == "aic" else (lambda k: k * math.log(n))
    scores = []
    for name, (sse, k) in models.items():
        scores.append((name, n * math.log(sse / n) + penalty(k)))
    scores.sort(key=lambda item: (item[1], item[0]))     # lowest first, ties by name
    return [(name, round(score, 4)) for name, score in scores]
