---
id: s4-02-backtesting
title: Backtesting with walk-forward windows
minutes: 30
level: intermediate
goals: [Explain expanding and sliding windows, Run a walk-forward backtest with many origins, Add a gap and read errors by horizon step]
prereqs: [s4-01-time-split-and-leakage]
tags: [evaluation, backtest, walk-forward]
skills: [backtest, leakage]
---
## Warm-up
```check
{"q": "Which split is correct for time series?", "type": "single",
 "options": ["Shuffle, then 80/20", "Train on the past, test on the future", "Train on the future, test on the past"],
 "answer": 1,
 "why": ["Shuffling leaks the future into training.", "Correct: the test set must come after the training set.", "This reverses time. Real use never works like that."]}
```

```check
{"q": "You fit a scaler on all data before splitting. What is this called?", "type": "single",
 "options": ["Regularization", "Data leakage", "Differencing"],
 "answer": 1,
 "why": ["Regularization limits model size. It is a different idea.", "Correct: the test period shaped the scaler.", "Differencing removes trend. It is not related."]}
```

## Why it matters
One train/test split gives **one** number. That number can be lucky. Maybe the test month had no holiday. Maybe it was calm. A [[backtest]] repeats the test many times in the past. Each time you pretend to stand at a different date and forecast ahead. The average over many tests is far more reliable. It also shows if the error grows when the world changes.

## Forecast origin and horizon
Two words you must know.

- The [[forecast origin]] is the last date you know when you make the forecast. After this date the data is hidden.
- The [[horizon]] is how many steps ahead you predict. Horizon 7 on daily data means 7 days.

Example: origin = day 100, horizon = 3. You train with days 1 to 100. You predict days 101, 102, 103. You compare with the true values. Then you **move the origin** forward and do it again.

```widget
{"name": "walk-forward", "params": {}}
```

```check
{"q": "Origin = day 50, horizon = 7. Which days do you predict?", "type": "single",
 "options": ["Days 43 to 49", "Days 51 to 57", "Days 50 to 56"],
 "answer": 1,
 "why": ["These are before the origin. They are known.", "Correct: you predict the 7 days after the origin.", "Day 50 is the origin. It is already known."]}
```

## Expanding window or sliding window
You have two ways to choose the training data at each origin.

| Type | Training data | When to use |
|---|---|---|
| **[[expanding window|Expanding window]]** | All data from the start up to the origin | Old data is still useful; the pattern is stable |
| **[[sliding window|Sliding window]]** | Only the last `W` points before the origin | The world changes; old data hurts; you need equal cost per fold |

An expanding window grows each fold. A sliding window keeps the same size and moves. Pick the one you will use in production. If you retrain on all history every week, use expanding. If you keep only the last year, use sliding.

```check
{"q": "Your shop changed its prices a lot. Data from 3 years ago is no longer typical. Which backtest style fits better?", "type": "single",
 "options": ["Expanding window", "Sliding window", "Random window"],
 "answer": 1,
 "why": ["It keeps the old data, which may now be misleading.", "Correct: a sliding window forgets old behaviour.", "Random windows break time order."]}
```

## Walk-forward and many origins
**[[walk-forward validation|Walk-forward validation]]** moves the origin step by step. The `step` is how far the origin moves each time. With `step = 1` and daily data, you test every day. With `step = horizon`, test windows do not overlap.

Plan the folds with three numbers: `initial` (size of the first training set), `horizon`, and `step`.

Example: 30 points, `initial = 20`, `horizon = 4`, `step = 4`.

- Fold 1 ([[fold]] = one train/test round): train points 0 to 19, test points 20 to 23.
- Fold 2: train points 0 to 23, test points 24 to 27.
- A third fold would need points 28 to 31. We only have 30. So we stop.

Only count **complete** folds. A fold with a short test window is not comparable.

```check
{"q": "30 points, initial = 20, horizon = 4, step = 2. How many complete folds?", "type": "numeric",
 "answer": 4, "tol": 0.001,
 "why": "Test windows start at 20, 22, 24, 26. Start 26 covers 26 to 29, so it fits. Start 28 would need point 31. So 4 folds."}
```

## Gap (embargo) and horizon-wise errors
A **[[embargo|gap]]** skips some points between the training end and the test start. Use it when the last training labels depend on the first test days. Example: a label is a 7-day sum, or data arrives 2 days late in production. If production has a delay of 2 days, your backtest must have a gap of 2 too.

Finally, do not average over all horizon steps at once. Compute the error **for each horizon step** (step 1, step 2, ..., step h). Errors usually grow with the horizon. A table by horizon tells you how far ahead the model is useful.

```chart
{"title": "Typical error grows with the forecast step", "x": "horizon step", "height": 200,
 "series": [
   {"name": "model MAE", "y": [1.0, 1.3, 1.5, 1.8, 1.9, 2.2, 2.4]},
   {"name": "naive MAE", "y": [1.6, 1.9, 2.1, 2.4, 2.5, 2.7, 2.8], "dash": true}
 ],
 "caption": "The model beats naive at every step, but the gap shrinks later. Illustration with made-up numbers."}
```

```check
{"q": "In production, data for day t arrives on day t+2. You forecast at the end of day t+2 for the days after. What does the backtest need?", "type": "single",
 "options": ["A gap of 2 days between train and test", "A bigger horizon", "No change"],
 "answer": 0,
 "why": ["Correct: the real model cannot see the last 2 days, so the backtest must hide them too.", "The horizon is a business choice, not a fix for delay.", "Without the gap, the backtest uses data that production does not have."]}
```

## Worked example
We write a small splitter and a walk-forward evaluator. The data has a weekly pattern. We compare **naive** (last value) with **[[seasonal naive]]** (value 7 days ago) by horizon step.

```python
import numpy as np

def backtest_splits(n, initial, horizon, step=None, window=None, gap=0):
    """Yield (train_idx, test_idx) for every complete fold."""
    step = step or horizon
    end = initial                       # exclusive end of the training part
    while end + gap + horizon <= n:     # only complete folds
        start = 0 if window is None else max(0, end - window)
        yield np.arange(start, end), np.arange(end + gap, end + gap + horizon)
        end += step

def walk_forward_mae(y, forecaster, initial, horizon, step=1):
    errs = []
    for tr, te in backtest_splits(len(y), initial, horizon, step):
        pred = forecaster(y[tr], horizon)          # use the training part only
        errs.append(np.abs(y[te] - pred))          # one row per fold
    return np.mean(errs, axis=0)                   # mean over folds, per step

def naive(train, h):
    return np.full(h, train[-1])

def seasonal_naive(train, h, m=7):
    return np.array([train[-m + (i % m)] for i in range(h)])

rng = np.random.default_rng(1)
t = np.arange(140)
y = 50 + 10 * np.sin(2 * np.pi * t / 7) + rng.normal(0, 1, 140)

folds = list(backtest_splits(30, 20, 4, step=4))
print("folds for n=30:", [(int(f[0][-1]), int(f[1][0])) for f in folds])
print("naive by step:", walk_forward_mae(y, naive, 70, 3).round(2))
print("seasonal naive by step:", walk_forward_mae(y, seasonal_naive, 70, 3).round(2))
# Output:
# folds for n=30: [(19, 20), (23, 24)]
# naive by step: [ 5.41  9.94 12.5 ]
# seasonal naive by step: [1.08 1.05 1.05]
```

Seasonal naive wins at every step, because the series has a weekly pattern. The naive error is large because the value changes a lot from day to day.

## Common mistakes
- One single split and a strong claim. Use several origins.
- Training on the whole history in each fold when production uses a sliding window (or the reverse).
- Forgetting the data delay: no gap, so the backtest is too optimistic.
- Averaging all horizon steps together. Report the error for each step or for the business horizon.
- Counting incomplete folds at the end of the data.
- Tuning hyperparameters on the same folds you report. Keep a final period for the last check.

## Interview lens
**Typical question:** "How would you validate a model that forecasts the next 14 days of demand?"

**Strong answer:** I use a rolling-origin (walk-forward) backtest. I choose the first training size, then move the origin every week so that I get many folds. Each fold forecasts 14 days, and I compute the error for each horizon step. I match production: if I retrain on all data, I use an expanding window; if there is a data delay, I add a gap. I compare with a seasonal naive baseline in the same folds. At the end I report the mean and the spread across folds.

**Red flags:** "I used one 80/20 split"; "cross-validation with shuffle"; no baseline; hiding the horizon in a single average; peeking at the last fold while tuning.

## Real world
- scikit-learn offers `TimeSeriesSplit`, an expanding-window splitter. It also has `gap` and `max_train_size` for a gap and a sliding window.
- Hyndman and Athanasopoulos call this method "time series cross-validation" in their free book *Forecasting: Principles and Practice*. Many forecasting libraries (for example Darts, sktime, StatsForecast) have a built-in backtest or cross-validation function.
- The M5 competition used a hidden period after the training data, which is one long test window; teams built their own multi-origin backtests to pick models.

## Key points
- A backtest repeats the forecast at many origins to get a reliable error.
- Expanding window keeps all history; sliding window keeps the last `W` points.
- Use `initial`, `horizon`, `step` to plan folds. Count only complete folds.
- A gap copies real delays in data or labels. Report errors per horizon step.
