import numpy as np
import pandas as pd


def classify_demand(y):
    y = np.asarray(y, dtype=float)
    pos = y[y > 0]
    if len(pos) == 0:
        return {"adi": None, "cv2": None, "class": "no demand"}
    adi = len(y) / len(pos)                       # average periods between demands
    cv2 = (np.std(pos) / np.mean(pos)) ** 2       # variation of the demand sizes only
    if adi <= 1.32:
        name = "smooth" if cv2 <= 0.49 else "erratic"
    else:
        name = "intermittent" if cv2 <= 0.49 else "lumpy"
    return {"adi": round(float(adi), 4), "cv2": round(float(cv2), 4), "class": name}


def classify_table(df):
    rows = {col: classify_demand(df[col].to_numpy()) for col in df.columns}
    return pd.DataFrame.from_dict(rows, orient="index")[["adi", "cv2", "class"]]
