import numpy as np
import pandas as pd

B1 = pd.DataFrame({"store": ["S1", "S1", "S2"], "dept": ["A", "B", "A"], "revenue": [30.0, 10.0, 60.0]})
L1 = [[], ["store"], ["store", "dept"]]
B2 = pd.DataFrame({"store": ["S1", "S2"], "dept": ["A", "A"], "revenue": [0.0, 0.0]})
rng = np.random.default_rng(3)
B3 = pd.DataFrame({"state": rng.choice(["CA", "TX", "WI"], 40), "store": rng.choice(["a", "b", "c", "d"], 40),
                   "revenue": rng.uniform(0, 100, 40)}).drop_duplicates(["state", "store"])
L3 = [[], ["state"], ["state", "store"]]
TR = list(np.concatenate([np.zeros(10), rng.poisson(3, 200)]))

CASES = [
    {"name": "tiny hierarchy weights", "call": "hierarchy_weights(B1, L1)", "visible": True,
     "expected": "pd.DataFrame({'level': [0,1,1,2,2,2], 'key': ['Total','S1','S2','S1/A','S1/B','S2/A'], 'weight': [1.0,0.4,0.6,0.3,0.1,0.6]})"},
    {"name": "rmsse example", "call": "rmsse([0, 0, 2, 4, 6], [8, 10], [7, 12])", "expected": "math.sqrt(2.5 / 4)", "visible": True},
    {"name": "zero revenue gives zero weights", "call": "hierarchy_weights(B2, [[], ['store']])",
     "expected": "pd.DataFrame({'level': [0,1,1], 'key': ['Total','S1','S2'], 'weight': [0.0,0.0,0.0]})"},
    {"name": "constant history has no scale", "call": "rmsse([5, 5, 5], [5], [4])", "expected": "float('nan')"},
    {"name": "all zero history", "call": "rmsse([0, 0, 0], [1], [1])", "expected": "float('nan')"},
    {"name": "single non-zero point", "call": "rmsse([0, 0, 3], [1], [1])", "expected": "float('nan')"},
    {"name": "weights random: each level sums to 1", "call": "hierarchy_weights(B3, L3)"},
    {"name": "rmsse random", "call": "rmsse(TR, list(rng.poisson(3, 28)), list(rng.poisson(3, 28)))"},
]
