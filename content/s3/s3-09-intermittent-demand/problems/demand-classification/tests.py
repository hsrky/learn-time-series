import numpy as np
import pandas as pd

_r = np.random.default_rng(18)
DF = pd.DataFrame({
    "A": [10, 12, 9, 11, 10, 12, 11, 9],
    "B": [0, 0, 5, 0, 0, 0, 3, 0],
    "C": [1, 30, 2, 25, 1, 40, 3, 0],
    "D": [0, 0, 0, 0, 0, 0, 0, 0],
    "E": [0, 1, 0, 0, 90, 0, 0, 2],
})


def check(got, exp, case):
    if isinstance(exp, dict):
        if got.get("class") != exp["class"]:
            return False, f"expected class {exp['class']}, got {got.get('class')}"
        for k in ("adi", "cv2"):
            if (got[k] is None) != (exp[k] is None) or (got[k] is not None and abs(got[k] - exp[k]) > 1e-3):
                return False, f"expected {exp}, got {got}"
        return True, ""
    if isinstance(exp, pd.DataFrame):
        if list(got.index) != list(exp.index) or list(got["class"]) != list(exp["class"]):
            return False, "index or classes differ"
        ok = np.allclose(got[["adi", "cv2"]].astype(float).fillna(-1), exp[["adi", "cv2"]].astype(float).fillna(-1), atol=1e-3)
        return bool(ok), "" if ok else "adi/cv2 values differ"
    return got == exp, "" if got == exp else f"expected {exp}"


CASES = [
    {"name": "intermittent example", "call": "classify_demand([0, 0, 5, 0, 0, 0, 3, 0, 4])", "visible": True},
    {"name": "smooth example", "call": "classify_demand([10, 12, 9, 11])", "visible": True},
    {"name": "no demand", "call": "classify_demand([0, 0, 0])"},
    {"name": "erratic", "call": "classify_demand([1, 40, 2, 35, 1, 50])"},
    {"name": "lumpy", "call": "classify_demand([0, 0, 1, 0, 0, 60, 0, 0, 0, 2])"},
    {"name": "ADI just above the cut-off (1.333)", "call": "classify_demand([5, 5, 5, 0] * 25)['class']", "expected": "'intermittent'"},
    {"name": "table", "call": "classify_table(DF)"},
]
