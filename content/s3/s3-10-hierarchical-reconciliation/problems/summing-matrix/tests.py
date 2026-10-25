import numpy as np

TREE2 = {"Total": ["A", "B"], "A": ["A1", "A2"], "B": ["B1", "B2"]}
UNEVEN = {"All": ["East", "West", "Online"], "East": ["NY", "MA"], "NY": ["NYC", "Buffalo"]}
FLAT = {"T": ["a", "b", "c", "d"]}
_r = np.random.default_rng(3)
BIG = {"root": [f"r{i}" for i in range(5)]}
for _i in range(5):
    BIG[f"r{_i}"] = [f"r{_i}s{j}" for j in range(6)]

CASES = [
    {"name": "one level", "call": "summing_matrix({'Total': ['A', 'B']}, 'Total')", "visible": True},
    {"name": "bottom-up", "call": "bottom_up([[1, 1], [1, 0], [0, 1]], [30, 20])", "visible": True},
    {"name": "three levels", "call": "summing_matrix(TREE2, 'Total')"},
    {"name": "uneven tree (leaves at different depths)", "call": "summing_matrix(UNEVEN, 'All')"},
    {"name": "flat tree, row sums", "call": "np.array(summing_matrix(FLAT, 'T')['S']).sum(axis=1).tolist()", "expected": "[4, 1, 1, 1, 1]"},
    {"name": "single node", "call": "summing_matrix({}, 'Only')"},
    {"name": "bottom-up on three levels", "call": "bottom_up(summing_matrix(TREE2, 'Total')['S'], [30, 26, 22, 18])"},
    {"name": "larger tree: shape", "call": "np.array(summing_matrix(BIG, 'root')['S']).shape", "expected": "(36, 30)"},
    {"name": "larger tree: Total row is all ones", "call": "int(np.array(summing_matrix(BIG, 'root')['S'])[0].sum())", "expected": "30"},
]
