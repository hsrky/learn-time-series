import numpy as np
rng = np.random.default_rng(5)
def _events(k):
    starts = np.sort(rng.choice(np.arange(0, 100000, 20), size=k, replace=False))
    return [(int(s), int(s) + int(rng.integers(0, 15))) for s in starts]
BT = _events(2000)
BP = _events(2500)
CASES = [
    {"name": "mixed", "call": "event_precision_recall([(10, 20), (40, 50), (70, 75)], [(18, 22), (45, 46), (60, 62), (90, 91)])", "visible": True},
    {"name": "perfect", "call": "event_precision_recall([(1, 3), (8, 9)], [(1, 3), (8, 9)])", "visible": True},
    {"name": "no predictions", "call": "event_precision_recall([(1, 3)], [])"},
    {"name": "no true events", "call": "event_precision_recall([], [(1, 3)])"},
    {"name": "touching ends overlap", "call": "event_precision_recall([(5, 10)], [(10, 12), (0, 5)])"},
    {"name": "one long alarm covers two events", "call": "event_precision_recall([(1, 2), (5, 6)], [(0, 10)])"},
    {"name": "unsorted input", "call": "event_precision_recall([(50, 60), (1, 5)], [(55, 56), (2, 3), (100, 101)])"},
    {"name": "random larger case", "call": "event_precision_recall(BT, BP)"},
]
