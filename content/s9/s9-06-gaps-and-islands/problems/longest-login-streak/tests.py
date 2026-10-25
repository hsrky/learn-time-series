import datetime as dt
import numpy as np
rng = np.random.default_rng(24)
_base = dt.date(2023, 1, 1).toordinal()
BIG = [dt.date.fromordinal(_base + int(v)).isoformat() for v in rng.integers(0, 3000, 2000)]
CASES = [
    {"name": "with duplicate", "call": "longest_streak(['2024-03-01', '2024-03-02', '2024-03-02', '2024-03-03', '2024-03-05'])", "visible": True},
    {"name": "empty", "call": "longest_streak([])", "visible": True},
    {"name": "single day", "call": "longest_streak(['2024-01-01'])"},
    {"name": "across a leap day", "call": "longest_streak(['2024-02-28', '2024-03-01', '2024-02-29', '2023-12-31'])"},
    {"name": "tie goes to the earlier run", "call": "longest_streak(['2024-05-10', '2024-05-11', '2024-05-01', '2024-05-02'])"},
    {"name": "across a year end", "call": "longest_streak(['2023-12-30', '2023-12-31', '2024-01-01', '2024-01-02', '2024-01-04'])"},
    {"name": "random larger case", "call": "longest_streak(BIG)"},
]
