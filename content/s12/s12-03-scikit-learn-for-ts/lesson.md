---
id: s12-03-scikit-learn-for-ts
title: scikit-learn for time series: splits, pipelines and boosting
minutes: 30
level: intermediate
goals: [Use TimeSeriesSplit with a gap and explain why shuffling is wrong, Build a Pipeline that avoids scaling leakage, Use HistGradientBoostingRegressor with lag features and know its limits]
prereqs: [s12-02-statsmodels-models]
tags: [scikit-learn, TimeSeriesSplit, pipeline, HistGradientBoosting, lag-features, leakage]
skills: [scikit-learn, backtesting, leakage-free-features, lag-features]
---

## Warm-up

```check
{"q": "A lower AIC is better only when...", "type": "single",
 "options": ["The models are fitted to the same data", "The models use different data", "The series is seasonal"],
 "answer": 0,
 "why": ["Correct.", "AIC values are not comparable across different data.", "Season is not the condition."]}
```

```check
{"q": "What does a Ljung-Box p-value of 0.001 on residuals say?", "type": "single",
 "options": ["Residuals still have autocorrelation", "Residuals are white noise", "The data are stationary"],
 "answer": 0,
 "why": ["Correct.", "White noise would give a large p-value.", "The test does not check stationarity."]}
```

## Why it matters

Most real forecasting systems at large scale are **machine learning on a table**: lag features in columns, a gradient-boosting model, and a good validation scheme. scikit-learn is the standard Python toolkit for that. It has no forecasting model, but it has everything around it: splitters, pipelines, metrics, and a fast boosting model. The most common mistake in interviews is to use scikit-learn tools made for ordinary data (random split, `KFold(shuffle=True)`) on time series. This lesson shows the right tools. Everything here **runs in your browser** in the problems of this stage.

## From series to a table

scikit-learn needs a table `X` (features) and a vector `y` (target). For a series you build the features yourself with `shift`:

```python
df["lag1"] = df["y"].shift(1)                       # yesterday
df["lag7"] = df["y"].shift(7)                       # same day last week
df["roll7"] = df["y"].shift(1).rolling(7).mean()    # mean of the last 7 days, ending yesterday
df = df.dropna()
```

Note the `shift(1)` **before** `rolling`: the window must end at yesterday, otherwise today's value is inside its own feature (leakage).

```widget
{"name": "lag-features", "params": {}}
```

```check
{"q": "Which line builds a leak-free 7-day rolling mean feature for time t?", "type": "single",
 "options": ["y.rolling(7).mean()", "y.shift(1).rolling(7).mean()", "y.rolling(7, center=True).mean()", "y.shift(-1).rolling(7).mean()"],
 "answer": 1,
 "why": ["The window includes y[t], the value we predict.", "Correct: the window ends at t-1.", "A centered window looks into the future.", "shift(-1) moves future values backwards in time."]}
```

## TimeSeriesSplit and why shuffle=False

**`TimeSeriesSplit(n_splits, gap, test_size, max_train_size)`** gives expanding-window splits: each fold trains on the past and tests on the next block. There is no shuffle option, and the rows must be in time order.

- `gap=g` leaves `g` rows between the end of training and the start of the test block. Use it when your features or targets use windows that overlap (a 7-day rolling target, or a 7-step ahead forecast).
- `test_size` fixes the size of each test block.
- `max_train_size` makes it a sliding window.

Why not `KFold(shuffle=True)` or `train_test_split` with its default (`shuffle=True`)? Because neighbours in time are similar. A shuffled split puts day 100 in training and day 101 in the test set, so the model "knows" the answer. The score is too good, and the real forecast is worse. If you must use `train_test_split` on ordered data, set `shuffle=False`.

```check
{"q": "You use KFold(5, shuffle=True) on lag features and get MAE 1.2. A walk-forward test gives 2.0. Which number do you report as the expected error?", "type": "single",
 "options": ["1.2", "2.0", "The average of both", "Neither; they are the same"],
 "answer": 1,
 "why": ["Shuffled validation leaks neighbouring days, so it is too optimistic.", "Correct: the walk-forward score copies how the model will be used.", "Averaging mixes a wrong number with a right one.", "They differ because of the leak."]}
```

## Pipelines: no leakage from preprocessing

A **`Pipeline`** chains steps (for example `StandardScaler` then `Ridge`). When you pass a pipeline to `cross_val_score`, scikit-learn fits the scaler **only on each training fold**. If you scale the whole table first, the mean and standard deviation of the future test rows leak into training.

```python
pipe = Pipeline([("scale", StandardScaler()), ("ridge", Ridge(alpha=1.0))])
scores = cross_val_score(pipe, X, y, cv=TimeSeriesSplit(5, gap=7), scoring="neg_mean_absolute_error")
```

Scores named `neg_...` are negative, because scikit-learn maximises scores. Use `-scores.mean()`.

## HistGradientBoostingRegressor

**`HistGradientBoostingRegressor`** is a fast gradient-boosting model, similar to LightGBM. It handles missing values (NaN) in features, supports categorical features and quantile loss (`loss="quantile", quantile=0.9`), and scales to many rows.

Three points for time series:

1. **Early stopping.** By default it is switched on for more than 10 000 rows, and it uses a **random** validation split, which leaks time. Set `early_stopping=False`, or use your own time-based validation.
2. **Trees do not extrapolate.** A tree predicts values it saw in training. With a strong trend or a random walk, the next value is outside the training range, and the forecast lags behind. Fix it by predicting the **difference** `y[t] − y[t-1]` (or the ratio), or by adding a linear model.
3. **Multi-step forecasts** need a strategy: **recursive** (feed predictions back, as in the practice problem), or **direct** (one model per horizon, for example with `MultiOutputRegressor`).

```check
{"q": "Why can a tree model fail on a series with a strong upward trend?", "type": "single",
 "options": ["Trees are too slow", "Tree predictions stay inside the range of training targets, so they cannot continue the trend", "Trees cannot use lag features", "Trees need scaling"],
 "answer": 1,
 "why": ["Speed is not the problem.", "Correct: a tree outputs averages of training targets.", "Lag features work well with trees.", "Trees do not need scaling."]}
```

## Worked example

We compare three things on the same lag-feature table: the honest walk-forward score of a boosting model, the too-good score from shuffled KFold, and a scaled Ridge pipeline. We also print the splits of `TimeSeriesSplit(gap=2)` for 12 rows.

```python
import numpy as np
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit, KFold, cross_val_score
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge

for k, (tr, te) in enumerate(TimeSeriesSplit(n_splits=3, gap=2).split(np.arange(12).reshape(-1, 1))):
    print(f"fold {k}: train {tr.tolist()}  test {te.tolist()}")

rng = np.random.default_rng(0)
n = 400
t = np.arange(n)
y = pd.Series(20 + 0.05 * t + 5 * np.sin(2 * np.pi * t / 7) + np.cumsum(rng.normal(0, 0.8, n)))
df = pd.DataFrame({"y": y})
for k in (1, 2, 3, 7):
    df[f"lag{k}"] = df["y"].shift(k)                       # lag features
df["roll7"] = df["y"].shift(1).rolling(7).mean()           # leak-free rolling mean
df = df.dropna()
X, target = df.drop(columns="y"), df["y"]

model = HistGradientBoostingRegressor(max_iter=150, early_stopping=False, random_state=0)
good = cross_val_score(model, X, target, cv=TimeSeriesSplit(n_splits=5, gap=7), scoring="neg_mean_absolute_error")
bad = cross_val_score(model, X, target, cv=KFold(n_splits=5, shuffle=True, random_state=0), scoring="neg_mean_absolute_error")
print("MAE with TimeSeriesSplit (gap=7):", round(-good.mean(), 2))
print("MAE with shuffled KFold         :", round(-bad.mean(), 2))

pipe = Pipeline([("scale", StandardScaler()), ("ridge", Ridge(alpha=1.0))])
ridge = cross_val_score(pipe, X, target, cv=TimeSeriesSplit(n_splits=5, gap=7), scoring="neg_mean_absolute_error")
print("Ridge pipeline MAE, TimeSeriesSplit:", round(-ridge.mean(), 2))
# Output:
# fold 0: train [0]  test [3, 4, 5]
# fold 1: train [0, 1, 2, 3]  test [6, 7, 8]
# fold 2: train [0, 1, 2, 3, 4, 5, 6]  test [9, 10, 11]
# MAE with TimeSeriesSplit (gap=7): 1.98
# MAE with shuffled KFold         : 1.22
# Ridge pipeline MAE, TimeSeriesSplit: 0.78
```

Three lessons from the numbers. First, the shuffled split reports a much smaller error than the honest one: it is leaking. Second, the first fold of `TimeSeriesSplit` has a tiny training set, which is normal for an expanding window. Third, on this random-walk-like series the simple Ridge pipeline is better than boosting, because trees cannot extrapolate. A better boosting setup would predict the difference.

## Common mistakes

- Random split or `KFold(shuffle=True)` on a time series.
- Scaling or imputing on the whole data before the split. Put these steps in a `Pipeline`.
- Rolling features whose window includes the current row.
- Leaving automatic early stopping on (random validation split).
- No `gap` when the target looks several steps ahead or features overlap.
- Using HistGradientBoosting on a trending series without differencing.
- Forgetting that `neg_mean_absolute_error` is negative.

## Interview lens

**Typical question:** "How do you cross-validate a time-series model in scikit-learn?"

**Strong answer:** I never shuffle. I build lag and rolling features with shift so each window ends before the row, put preprocessing in a Pipeline, and validate with `TimeSeriesSplit`, using a `gap` when features or targets overlap and `test_size` equal to the forecast horizon. I use `HistGradientBoostingRegressor` with `early_stopping=False`, and I difference the target if there is a trend, because trees cannot extrapolate. I compare the score with a seasonal naive baseline. For multi-step forecasts I choose between a recursive and a direct strategy.

**Red flags:** `train_test_split` with the default shuffle. Scaling before splitting. Not knowing the gap argument.

## Real world

scikit-learn's `TimeSeriesSplit` is based on the common "rolling origin" idea described in forecasting textbooks. Gradient boosting with lag features was the standard winning approach in many forecasting competitions, such as the M5 on Kaggle. Libraries such as skforecast, mlforecast and sktime wrap these patterns, but under the hood they use the same scikit-learn estimators.

## Key points

- Build features with `shift`; shift before rolling.
- `TimeSeriesSplit(n_splits, gap, test_size)` is the right splitter. Shuffling leaks the future.
- Put preprocessing in a `Pipeline` so each fold fits it on training data only.
- `HistGradientBoostingRegressor`: set `early_stopping=False`, difference trending targets, choose a multi-step strategy.
- Use `neg_mean_absolute_error` and flip the sign.
