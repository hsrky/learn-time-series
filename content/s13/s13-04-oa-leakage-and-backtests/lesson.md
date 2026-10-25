---
id: s13-04-oa-leakage-and-backtests
title: OA patterns - leakage-free features, metrics and backtests
minutes: 35
level: intermediate
goals: [Build a rolling feature that never sees today, Write WAPE and MAE from scratch and avoid ratio mistakes, Run a seasonal naive backtest with several folds, Spot the three classic leakage bugs in a code review]
prereqs: [s13-03-oa-pandas-wrangling]
tags: [leakage, backtest, metrics, rolling, OA]
skills: [leakage, backtest, metrics, from-scratch]
---

## Warm-up

```check
{"q": "What does series.shift(1) do?", "type": "single",
 "options": ["Moves every value one step later, so each row holds the previous value", "Removes the first row", "Doubles each value", "Sorts the series"],
 "answer": 0,
 "why": ["Correct: row t now holds the value from t-1.", "It keeps the length and puts NaN at the start.", "It does not change values.", "It never sorts."]}
```

```check
{"q": "What is the aim of a backtest?", "type": "single",
 "options": ["To make the training faster", "To measure how a method would have forecast in the past, using only data available then", "To remove outliers", "To choose a colour palette"],
 "answer": 1,
 "why": ["Backtests measure error, not speed.", "Correct: we replay history honestly, one forecast origin at a time.", "Outlier handling is separate.", "Not related."]}
```

## Why it matters

Three kinds of OA problems come back all the time: build a feature, compute a metric, run a backtest. All three have one hidden trap: **[[data leakage]]**. A leaked feature gives a score that is too good. In an OA the hidden tests catch it. In a real job it costs money. This lesson shows the three classic bugs and the clean code for each.

## Bug 1: the rolling window that sees today

Suppose you predict today's sales. You make a feature: mean of the last 3 days. If your rolling window **includes today**, it contains the answer.

Look at the chart. The leaky line follows the real values closely. The safe line lags behind, because it only knows the past.

```chart
{"title": "Rolling mean of 3 days: with today (leaky) vs shifted (safe)", "x": "day", "height": 230,
 "series": [
   {"name": "actual", "x": [1,2,3,4,5,6,7,8,9,10,11,12], "y": [10,12,9,14,11,13,15,12,16,14,17,15]},
   {"name": "leaky: includes today", "x": [1,2,3,4,5,6,7,8,9,10,11,12], "y": [10,11,10.33,11.67,11.33,12.67,13,13.33,14.33,14,15.67,15.33], "dash": true},
   {"name": "safe: shift(1) first", "x": [2,3,4,5,6,7,8,9,10,11,12], "y": [10,11,10.33,11.67,11.33,12.67,13,13.33,14.33,14,15.67], "dash": true}
 ],
 "caption": "The safe feature starts one day later and uses only earlier days."}
```

The fix is one word: **shift first, then roll**. `s.shift(1).rolling(3).mean()`. Do it per group with `groupby(...).transform(...)`. Practise in [[problem:rolling-mean-per-store-no-leak]].

```check
{"q": "Which line builds a leakage-free 7-day mean for each store?", "type": "single",
 "options": ["df.groupby('store')['sales'].rolling(7).mean()", "df.groupby('store')['sales'].transform(lambda s: s.shift(1).rolling(7).mean())", "df['sales'].rolling(7).mean()", "df['sales'].shift(-1).rolling(7).mean()"],
 "answer": 1,
 "why": ["This rolls inside each store but includes today, and the index differs from the original.", "Correct: shift(1) removes today, groupby keeps stores apart, transform keeps the original index.", "No groups, and includes today.", "shift(-1) moves the future backward into the row: even worse."]}
```

## Bug 2: metrics with the wrong ratio

Two metrics you must write from scratch.

- **MAE** = mean of |actual − forecast|
- **WAPE** = sum of |actual − forecast| divided by sum of actual

WAPE is a ratio of **sums**. It is not the mean of the daily percentage errors. The two give different numbers. For weekly reports by group, first sum inside each group and week, then divide. Check the zero case: if the sum of actual is 0, return NaN. Practise in [[problem:weekly-wape-by-group]].

Also remember how to find the Monday of a week. Do not use `resample("W")` for it: that label is the Sunday at the **end** of the week.

```check
{"q": "A group has daily actuals [10, 0, 90] and absolute errors [5, 5, 9]. What is the WAPE?", "type": "numeric",
 "answer": 0.19, "tol": 0.005,
 "why": "Sum of errors = 5 + 5 + 9 = 19. Sum of actuals = 100. WAPE = 19 / 100 = 0.19. (Averaging daily percentage errors would fail because of the zero.)"}
```

## Bug 3: a backtest that uses the future

A **[[backtest]]** repeats the forecast at several **origins**. At each origin you train on the past and forecast the next `h` steps. A seasonal naive forecast repeats the last season. It is a strong baseline. Check these points:

- The training data stops **before** the test block.
- With `h` larger than the season `m`, the forecast must wrap around (use `i % m`).
- Average the errors over **all** folds, not only the last one.

Practise in [[problem:seasonal-naive-backtest]].

```widget
{"name": "walk-forward", "params": {}}
```

```check
{"q": "Series length 100, horizon 10, 4 folds, last 40 points are tested. At which positions do the test blocks start?", "type": "single",
 "options": ["60, 70, 80, 90", "0, 10, 20, 30", "10, 20, 30, 40", "90, 91, 92, 93"],
 "answer": 0,
 "why": ["Correct: the blocks cover positions 60-69, 70-79, 80-89, 90-99. Each block trains on everything before it.", "These are the first points; there would be no training history.", "These are far too early in the series.", "Folds must not overlap in this setting."]}
```

## Worked example

We show how large the leakage effect is. The target is pure random noise, so no honest feature can predict it. A good feature must have a correlation near 0.

```python
import numpy as np
import pandas as pd

rng = np.random.default_rng(0)
y = pd.Series(rng.normal(size=300))             # pure noise: nothing to predict

leaky = y.rolling(3).mean()                     # includes today -> contains y itself
safe = y.shift(1).rolling(3).mean()             # only days t-3, t-2, t-1

print("corr(y, leaky) =", round(y.corr(leaky), 3))
print("corr(y, safe)  =", round(y.corr(safe), 3))
# Output:
# corr(y, leaky) = 0.589
# corr(y, safe)  = 0.013
```

A feature with 0.59 correlation to pure noise is a red alarm. It shows the answer leaked in. The safe feature is near 0, as it should be for noise.

## Common mistakes

- `rolling(...)` without `shift(1)`.
- A global rolling window across stores.
- Scaling or filling missing values with statistics from the **whole** table before the split.
- Returning WAPE as a mean of daily percentage errors.
- `resample("W")` labels for weeks that start on Monday.
- Testing only one fold and calling it a backtest.
- Using `shift(-1)` by accident.

## Interview lens

**Typical question:** "Your offline MAE is excellent, but after launch the error doubles. What do you check?"

**Strong answer:** "I suspect leakage or a difference between offline and live data. I check every feature: is its value known at prediction time? Rolling windows must end before the forecast time. I check that scaling and imputation were fitted on the training part only. I check that the split is by time with a gap if the target is multi-step. Then I check that data used live arrives as early as it did in training, for example late-arriving sales."

**Red flags:** a random split; features built on the whole table; never listing the features with their time of availability.

## Real world

- A well-known rule in forecasting competitions is that the test period must be in the future of the training period. Kaggle forecasting competitions use a time-based hold-out for this reason. Leaks are a common cause of leaderboard shake-ups.
- Many companies describe "point-in-time correct" feature stores. They store each feature value with the time it became known. A training row can then join only values from before the forecast time.

## Key points

- Shift first, then roll: `s.shift(1).rolling(w).mean()`, per group with `transform`.
- WAPE is a ratio of sums; return NaN when the sum of actuals is zero.
- A backtest has several folds; training must end before each test block; wrap the season with `i % m`.
- A feature with a high score on random noise is a leakage alarm.
