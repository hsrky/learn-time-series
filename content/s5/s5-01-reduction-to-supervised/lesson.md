---
id: s5-01-reduction-to-supervised
title: Turning a series into a supervised table
minutes: 25
level: intermediate
goals: [Turn a series into a table with a sliding window, Count the rows and columns of the table, Keep the time order when you split the table]
prereqs: [s4-01-time-split-and-leakage]
tags: [ml, windows, supervised]
skills: [from-scratch, leakage]
---
## Warm-up
```check
{"q": "Which split is correct for a table made from a time series?", "type": "single",
 "options": ["Random rows", "Older rows for training, newer rows for testing", "Newer rows for training, older rows for testing"],
 "answer": 1,
 "why": ["Random rows leak the future into training.", "Correct: the test rows must come after the training rows.", "This reverses time."]}
```

```check
{"q": "What is the forecast horizon?", "type": "single",
 "options": ["The number of steps ahead you predict", "The length of the training data", "The size of the model"],
 "answer": 0,
 "why": ["Correct: horizon 7 means 7 steps ahead.", "That is the history length.", "The horizon is not about the model."]}
```

## Why it matters
Most [[supervised learning]] models (linear regression, random forest, gradient boosting) expect a **table**: each row is one example, each column is a [[feature]], and one column is the target. A time series is only one long column of numbers. To use the strong tools of machine learning, we must first **reshape** the series into a table. This idea is called [[reduction]]: we reduce forecasting to a normal supervised learning problem. The M5 winners and most Kaggle winners did exactly this.

## The sliding window
Take the series `y = 3, 5, 4, 6, 8, 7`. Choose a **window** of 3 values and a horizon of 1.

| Row | Feature 1 | Feature 2 | Feature 3 | Target |
|---|---|---|---|---|
| 1 | 3 | 5 | 4 | 6 |
| 2 | 5 | 4 | 6 | 8 |
| 3 | 4 | 6 | 8 | 7 |

- The **[[window]]** (also called lookback) is the number of past values used as features. Here `w = 3`.
- The target is the value `h` steps after the window. Here `h = 1`.
- We slide the window one step to the right to make the next row.

The number of rows is `n − w − h + 1`. Here `6 − 3 − 1 + 1 = 3`.

```chart
{"title": "Each row uses 3 past values to predict the next one", "x": "t", "height": 200,
 "series": [{"name": "y", "y": [3, 5, 4, 6, 8, 7]}],
 "marks": [{"x": 2, "label": "row 1 ends"}, {"x": 3, "label": "target of row 1"}],
 "caption": "Row 1 uses t = 0, 1, 2 as features and t = 3 (value 6) as the target."}
```

```check
{"q": "A series has 100 points. Window w = 10, horizon h = 1. How many rows does the table have?", "type": "numeric",
 "answer": 90, "tol": 0.001,
 "why": "n - w - h + 1 = 100 - 10 - 1 + 1 = 90."}
```

## Several steps ahead
If you need a forecast for the next `h = 3` steps, the target can have 3 columns: `y(t+1), y(t+2), y(t+3)`. This table has `n − w − h + 1` rows and `h` target columns. We will see in the lesson on multi-step strategies how models use it.

The window can use only values **before** the first target. This is the rule that keeps the table free of leakage: every feature value is older than every target value in the same row.

```check
{"q": "n = 20, w = 5, h = 3. How many rows?", "type": "numeric",
 "answer": 13, "tol": 0.001,
 "why": "20 - 5 - 3 + 1 = 13."}
```

## Split and fit
After building the table, the rest is normal machine learning, with one rule: **keep the time order**.

1. Build all windows from the whole history.
2. Row `i` belongs to training only if its target is at or before the cutoff.
3. Rows whose target is after the cutoff are test rows. Their features may contain values from the training period. This is fine: at forecast time those values are known.
4. Do not shuffle. Do not scale with the test rows.

Then fit a model (for example linear regression) and predict. To forecast the future, build one more row from the **last** `w` values and ask the model for the target.

```check
{"q": "The cutoff is day 80. A window row has features on days 76 to 78 and the target on day 81. Is it a training row?", "type": "single",
 "options": ["Yes, the features are before the cutoff", "No, its target is after the cutoff, so it is a test row", "Yes, if we shuffle the table"],
 "answer": 1,
 "why": ["The target is the part that must be hidden. Using it in training leaks the future.", "Correct: its target (day 81) lies after the cutoff.", "Shuffling is not allowed."]}
```

## What you gain and what you lose
Gain: you can use any model, add other features (calendar, price), and train on many series at once.

Lose: the model sees only the last `w` values. A long season (for example 365 days) needs a window of 365 or extra features. The model does not know about time order inside the window unless the columns keep their position. Most models give only a point forecast, so you need extra work for intervals (quantile objective or conformal).

## Worked example
We build the table with numpy, fit a linear model by least squares, and forecast the next value.

```python
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

y = np.array([3, 5, 4, 6, 8, 7, 9, 11, 10, 12], dtype=float)

def make_windows(y, w, h=1):
    """Return X (rows, w) and Y (rows, h). Rows = len(y) - w - h + 1."""
    n = len(y) - w - h + 1
    if n <= 0:
        return np.empty((0, w)), np.empty((0, h))
    X = sliding_window_view(y, w)[:n]          # features: w past values
    Y = sliding_window_view(y[w:], h)          # targets: the next h values
    return X, Y

X, Y = make_windows(y, 3, 1)
print("X shape:", X.shape, "Y shape:", Y.shape)
print("first two rows of X:", X[:2].tolist())
print("first two targets:", Y[:2].ravel().tolist())

# Fit linear regression with an intercept by least squares
A = np.c_[X, np.ones(len(X))]
coef, *_ = np.linalg.lstsq(A, Y, rcond=None)

# Forecast: build one more row from the LAST 3 values
last_row = np.r_[y[-3:], 1.0]
print("next value:", round((last_row @ coef).item(), 2))
# Output:
# X shape: (7, 3) Y shape: (7, 1)
# first two rows of X: [[3.0, 5.0, 4.0], [5.0, 4.0, 6.0]]
# first two targets: [6.0, 8.0]
# next value: 14.0
```

The model learns a rule from the three windows before. The forecast continues the upward move of the series.

## Common mistakes
- Shuffling the rows before the split.
- Building the windows after scaling on all data (leak).
- Off-by-one errors: the target must be after the last feature value.
- Forgetting that rows near the end have no target and cannot be training rows.
- Using a window that is too short for the season.
- Mixing up the number of rows with the number of points.

## Interview lens
**Typical question:** "How do you use a random forest for time series forecasting?"

**Strong answer:** I turn the series into a supervised table. Each row has the last `w` values as features, and the target is the value `h` steps ahead. I choose `w` by looking at the season and the autocorrelation. I split by time: older rows for training, newer rows for testing, and I never shuffle. I add calendar and other known features. For several steps ahead I use a recursive or a direct strategy. And I compare with a seasonal naive baseline in a walk-forward backtest.

**Red flags:** "Just call `train_test_split`"; not knowing how many rows the window creates; features that include the target value; no baseline.

## Real world
- Top solutions of the M5 forecasting competition used LightGBM on tables of lags and rolling statistics. This is the same reduction idea at scale.
- The libraries `mlforecast` (Nixtla), `sktime` and `skforecast` offer this reduction as a ready-made function.
- Pretrained time-series foundation models, such as Chronos, also work on windows of past values, but with a transformer instead of a table model.

## Key points
- Reduction turns a series into a table: the last `w` values are features, the next `h` values are targets.
- Rows = `n − w − h + 1`. Every feature is older than every target in its row.
- Split by time; build and scale using training data only.
- After that, any regression model can be used.
- The window length, the horizon strategy and extra features decide the quality.
