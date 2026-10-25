import numpy as np
import pandas as pd

rng = np.random.default_rng(2)
N = 300
T = ["t%03d" % i for i in range(N)]
PUB = list(np.round(rng.normal(0.5, 0.02, N), 3))      # rounding creates ties
PRI = list(np.round(rng.normal(0.5, 0.02, N), 3))

CASES = [
    {"name": "example", "call": "leaderboard_shakeup(['A','B','C'], [0.10,0.20,0.30], [0.40,0.20,0.10])", "visible": True,
     "expected": "pd.DataFrame({'team': ['C','B','A'], 'public_rank': [3,2,1], 'private_rank': [1,2,3], 'rank_change': [2,0,-2]})"},
    {"name": "ties share the best rank", "call": "leaderboard_shakeup(['b','a','c'], [0.5,0.5,0.7], [0.3,0.4,0.4])", "visible": True,
     "expected": "pd.DataFrame({'team': ['b','a','c'], 'public_rank': [1,1,3], 'private_rank': [1,2,2], 'rank_change': [0,-1,1]})"},
    {"name": "single team", "call": "leaderboard_shakeup(['solo'], [0.9], [0.1])",
     "expected": "pd.DataFrame({'team': ['solo'], 'public_rank': [1], 'private_rank': [1], 'rank_change': [0]})"},
    {"name": "empty", "call": "leaderboard_shakeup([], [], [])", "check_index": False},
    {"name": "identical boards", "call": "leaderboard_shakeup(['x','y','z'], [3,1,2], [3,1,2])",
     "expected": "pd.DataFrame({'team': ['y','z','x'], 'public_rank': [1,2,3], 'private_rank': [1,2,3], 'rank_change': [0,0,0]})"},
    {"name": "larger random with ties", "call": "leaderboard_shakeup(T, PUB, PRI)"},
]
