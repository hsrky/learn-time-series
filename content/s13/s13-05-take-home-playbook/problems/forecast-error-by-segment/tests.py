import numpy as np
import pandas as pd

D1 = pd.DataFrame({"segment": ["food", "food", "toys", "toys"], "actual": [100.0, 100.0, 10.0, 10.0], "forecast": [110.0, 90.0, 30.0, 10.0]})
D2 = pd.DataFrame({"segment": ["b", "a", "c", "a"], "actual": [0.0, 10.0, 5.0, 10.0], "forecast": [4.0, 14.0, 5.0, 6.0]})
D3 = pd.DataFrame({"segment": ["x", "y"], "actual": [5.0, 6.0], "forecast": [5.0, 6.0]})
D4 = pd.DataFrame({"segment": [], "actual": [], "forecast": []})
rng = np.random.default_rng(12)
D5 = pd.DataFrame({"segment": rng.choice(list("ABCDEFG"), 1000), "actual": rng.integers(0, 100, 1000).astype(float),
                   "forecast": rng.uniform(0, 100, 1000)})

CASES = [
    {"name": "example", "call": "error_by_segment(D1)", "visible": True,
     "expected": "pd.DataFrame({'segment': ['food','toys'], 'n': [2,2], 'wape': [0.1, 1.0], 'bias': [0.0, 1.0], 'share_of_error': [0.5, 0.5]})"},
    {"name": "zero actual segment, tie order", "call": "error_by_segment(D2)", "visible": True,
     "expected": "pd.DataFrame({'segment': ['a','b','c'], 'n': [2,1,1], 'wape': [0.4, np.nan, 0.0], 'bias': [0.0, np.nan, 0.0], 'share_of_error': [2/3, 1/3, 0.0]})"},
    {"name": "perfect forecast", "call": "error_by_segment(D3)",
     "expected": "pd.DataFrame({'segment': ['x','y'], 'n': [1,1], 'wape': [0.0, 0.0], 'bias': [0.0, 0.0], 'share_of_error': [0.0, 0.0]})"},
    {"name": "empty", "call": "error_by_segment(D4)", "check_index": False},
    {"name": "larger random", "call": "error_by_segment(D5)"},
]
