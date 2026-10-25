M = {"AR1": (120.0, 2), "AR3": (100.0, 4), "AR8": (95.0, 9)}


def err(f):
    try:
        f()
    except ValueError:
        return "ValueError"
    return "no error"


CASES = [
    {"name": "AIC ranking", "call": "rank_models(M, 50, 'aic')", "visible": True},
    {"name": "BIC ranking", "call": "rank_models(M, 50, 'bic')", "visible": True},
    {"name": "BIC prefers the smaller model on large n", "call": "[m for m, s in rank_models({'small': (1000.0, 2), 'big': (990.0, 6)}, 1000, 'bic')]", "expected": "['small', 'big']"},
    {"name": "AIC can prefer the bigger model", "call": "[m for m, s in rank_models({'small': (1000.0, 2), 'big': (900.0, 6)}, 1000, 'aic')]", "expected": "['big', 'small']"},
    {"name": "tie goes to the name order", "call": "rank_models({'b': (10.0, 2), 'a': (10.0, 2)}, 20, 'aic')"},
    {"name": "single model", "call": "rank_models({'only': (5.0, 3)}, 10, 'bic')"},
    {"name": "bad criterion", "call": "err(lambda: rank_models(M, 50, 'hqic'))", "expected": "'ValueError'"},
]
