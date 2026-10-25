import numpy as np
import pandas as pd

E1 = pd.DataFrame({"naive": [10.0, 4.0], "A": [8.0, 4.0], "B": [9.0, 3.0]}, index=["s1", "s2"])
E2 = pd.DataFrame({"naive": [5.0, 0.0, 2.0], "A": [4.0, 1.0, 2.0], "B": [6.0, 0.0, 1.0]}, index=list("xyz"))
E3 = pd.DataFrame({"naive": [5.0, 6.0, 7.0], "A": [4.0, np.nan, 7.0], "B": [3.0, 5.0, np.nan]}, index=list("pqr"))
rng = np.random.default_rng(31)
E4 = pd.DataFrame(rng.gamma(2.0, 5.0, size=(300, 4)), columns=["naive", "ets", "gbm", "nn"],
                  index=[f"s{i}" for i in range(300)])

CASES = [
    {"name": "two series example", "call": "compare_models(E1, 'naive')", "visible": True,
     "expected": "pd.DataFrame({'avg_rank': [2.75, 1.75, 1.5], 'rel_error': [1.0, 0.8 ** 0.5, 0.675 ** 0.5]}, index=['naive', 'A', 'B'])"},
    {"name": "zero baseline series is skipped", "call": "compare_models(E2, 'naive')", "visible": True},
    {"name": "NaN errors", "call": "compare_models(E3, 'naive')", "visible": True},
    {"name": "baseline compared with itself", "call": "compare_models(E1[['naive']], 'naive')",
     "expected": "pd.DataFrame({'avg_rank': [1.0], 'rel_error': [1.0]}, index=['naive'])"},
    {"name": "baseline in the middle column", "call": "compare_models(E1[['A', 'naive', 'B']], 'naive')"},
    {"name": "all ties", "call": "compare_models(pd.DataFrame({'a': [1.0, 2.0], 'b': [1.0, 2.0]}), 'a')",
     "expected": "pd.DataFrame({'avg_rank': [1.5, 1.5], 'rel_error': [1.0, 1.0]}, index=['a', 'b'])"},
    {"name": "larger random table", "call": "compare_models(E4, 'naive')"},
]
