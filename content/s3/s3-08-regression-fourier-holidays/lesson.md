---
id: s3-08-regression-fourier-holidays
title: Regression with trend, Fourier terms and holidays
minutes: 35
level: intermediate
goals: [Model a series as trend plus season plus holiday effects with linear regression, Build Fourier features for a season, Build holiday dummy features, Forecast with features known in advance, Explain the idea behind Prophet]
prereqs: [s3-05-autoregression, s3-01-baselines]
tags: [regression, fourier, holidays, prophet]
skills: [from-scratch, pandas-fluency]
---

## Warm-up

```check
{"q": "Which baseline suits a series with a strong weekly pattern?", "type": "single",
 "options": ["Seasonal naive with m = 7", "Mean", "Drift"],
 "answer": 0,
 "why": ["Correct: copy the value of the same weekday last week.", "The mean ignores the weekly shape.", "Drift follows a trend, not a pattern."]}
```

```check
{"q": "In a linear regression, what is a dummy variable?", "type": "single",
 "options": ["A column that is 1 when a condition is true and 0 otherwise", "A column of random numbers", "The target column"],
 "answer": 0,
 "why": ["Correct: for example 1 on holidays and 0 on other days.", "Random columns carry no information.", "A dummy is an input (feature), not the target."]}
```

## Why it matters

[[Exponential smoothing]] and [[ARIMA]] move through time step by step. There is another way: write the series as **parts that depend on the calendar**. Parts: a trend, a weekly pattern, a yearly pattern, and holiday effects. Then fit one linear regression. This model is easy to explain to a manager ("Christmas adds about 40 units"). It handles missing days and many seasons at once. It is the main idea behind **[[Prophet]]**, the library that Facebook released in 2017.

## The model

y(t) = trend(t) + seasonal(t) + holidays(t) + noise

- **trend(t):** a straight line a + b·t, or a line with bends ([[changepoint|changepoints]]).
- **seasonal(t):** a smooth repeating shape, built from [[Fourier terms]].
- **holidays(t):** extra effects on special days, built from dummy columns.
- **noise:** the part we cannot explain.

All parts are **features** (input columns). The model is a linear regression, so we fit it by [[least squares]], as in the AR lesson.

The big advantage: all features are known in the future, because they depend only on the date. For forecasting we just build the same columns for future dates. There is no recursion and no error that grows from step to step.

## Fourier terms: smooth seasons

A **Fourier term** is a sine or cosine wave with a chosen period P:

sin(2π·k·t / P) and cos(2π·k·t / P), for k = 1, 2, ..., K

- t: the time index (0, 1, 2, ...).
- P: the period (7 for a weekly cycle in daily data, 365.25 for a yearly cycle).
- k: the **harmonic**. k = 1 is one wave per period. k = 2 is two waves per period, and so on.
- K: how many harmonics we use. It sets the flexibility of the shape.

The regression finds one weight for each sin and cos column. The sum of the waves can make any smooth repeating shape. A bigger K gives a more detailed shape but may [[overfitting|overfit]]. For a weekly cycle K = 3 is already the full freedom (7 values need 2K = 6 columns plus the constant). For a yearly cycle K = 3 to 10 is common.

Numbers: P = 7, t = 1: sin(2π·1/7) = 0.78 and cos(2π·1/7) = 0.62.

```chart
{"title": "Fourier terms for a period of 7: k = 1 (sin and cos) and k = 2 (sin)", "x": "t", "height": 210,
 "series": [
  {"name": "sin k=1", "gen": [["season", {"period": 7, "amp": 1, "phase": 0}]], "n": 28},
  {"name": "cos k=1", "gen": [["season", {"period": 7, "amp": 1, "phase": 1.5708}]], "n": 28, "dash": true},
  {"name": "sin k=2", "gen": [["season", {"period": 3.5, "amp": 1, "phase": 0}]], "n": 28}
 ],
 "caption": "The regression mixes these waves with weights to draw the weekly shape."}
```

```check
{"q": "You use a weekly Fourier basis with K = 2 (period 7). How many columns do you add?", "type": "numeric",
 "answer": 4, "tol": 0.001,
 "why": "Each harmonic gives 2 columns (sin and cos). 2 harmonics give 4 columns."}
```

## Trend with changepoints

A single straight line is often too stiff. A **changepoint** is a time c where the slope changes. Add one column:

max(0, t − c)

It is 0 before c and grows linearly after c. Its weight is the **change of slope**. Several changepoints give a bent line (piecewise linear trend). Prophet places many and shrinks their weights so that only the important ones stay.

Numbers: c = 50. At t = 40 the column is 0. At t = 60 it is 10. If its weight is −0.2, the slope after t = 50 is 0.2 lower.

## Holidays and events

For each holiday, add a **dummy column**: 1 on the holiday dates and 0 on all other days. The weight is the holiday effect. Often you also add columns for the days **before** and **after**, because the effect spreads (the day before Christmas is busy).

Rules:

- Use a calendar of **dates** (the holiday moves in the week and in the month).
- List the holiday dates for the **future**, too. Otherwise the forecast cannot use them.
- Only add holidays with enough examples. One occurrence in the data cannot be estimated well.

```check
{"q": "Christmas Day is in the training data 3 times (2022, 2023, 2024). Sales are +40 on each. What is a good feature?", "type": "single",
 "options": ["A dummy that is 1 on December 25", "A feature with the sales of the last year", "No feature, treat it as noise"],
 "answer": 0,
 "why": ["Correct: the dummy learns the +40 effect and applies it to future Christmases.", "That would use the target in the features and still not mark the holiday.", "A regular +40 is not noise. A dummy captures it."]}
```

## Fit and forecast

1. Build the feature matrix for the training dates: constant, t, changepoints, Fourier terms, holiday dummies.
2. Solve the least squares problem.
3. Build the **same** features for the future dates and multiply by the weights.

Fit the model on the training part and measure the error on a later test part. Compare with [[seasonal naive]].

Weak points: the model assumes the seasonal shape is fixed. It does not use recent values of the series, so it can miss short-term momentum. You can add AR terms or use an ARIMA model on the [[residual|residuals]] (regression with ARIMA errors).

## Worked example

We create three years of daily sales with a trend, weekly and yearly seasons, and a Christmas effect. We fit by least squares and forecast the next 28 days.

```python
import numpy as np
import pandas as pd

rng = np.random.default_rng(8)
dates = pd.date_range("2022-01-01", periods=3 * 365 + 28, freq="D")
t = np.arange(len(dates))
xmas = pd.to_datetime(["2022-12-25", "2023-12-25", "2024-12-25"])
is_xmas = dates.isin(xmas).astype(float)
y = (200 + 0.05 * t + 20 * np.sin(2 * np.pi * t / 7) + 10 * np.cos(4 * np.pi * t / 7)
     + 15 * np.sin(2 * np.pi * t / 365.25) + 40 * is_xmas + rng.normal(0, 4, len(t)))

def fourier(t, period, K):
    cols = []
    for k in range(1, K + 1):
        cols += [np.sin(2 * np.pi * k * t / period), np.cos(2 * np.pi * k * t / period)]
    return np.column_stack(cols)

# Features: constant, trend, weekly (K=3), yearly (K=3), Christmas dummy
X = np.column_stack([np.ones(len(t)), t, fourier(t, 7, 3), fourier(t, 365.25, 3), is_xmas])
n = 3 * 365                                  # train: first 3 years; test: the next 28 days
beta, *_ = np.linalg.lstsq(X[:n], y[:n], rcond=None)
forecast = X[n:] @ beta                      # the features of future dates are known

snaive = np.tile(y[n - 7:n], 4)              # baseline: repeat the last week
mae = lambda f: np.mean(np.abs(y[n:] - f))
print("trend weight per day:", round(beta[1], 3), "(true 0.05)")
print("Christmas effect:", round(beta[-1], 1), "(true 40)")
print("regression MAE:", round(mae(forecast), 2))
print("seasonal naive MAE:", round(mae(snaive), 2))
# Output:
# trend weight per day: 0.05 (true 0.05)
# Christmas effect: 35.6 (true 40)
# regression MAE: 3.31
# seasonal naive MAE: 9.28
```

## Common mistakes

- Using a Fourier period that does not match the data (for example 365 for monthly data).
- Too many harmonics (K), which fit noise.
- Forgetting the holiday dates in the future.
- Building the features of the test period with information from the target.
- Using one yearly dummy for each day. Use a smooth Fourier basis instead.
- Comparing only with naive. For this kind of data use seasonal naive.

## Interview lens

**Typical question:** "How does Prophet work? Could you build a similar model yourself?"

**Strong answer:** Prophet models the series as a sum of three parts. The trend is piecewise linear (or saturating) with changepoints. The seasons are Fourier terms for weekly and yearly patterns. Holiday effects are dummy features. The fit uses a Bayesian method that shrinks the changepoint weights. I could build a simple version with ordinary least squares. I would use columns for time, hinge terms for changepoints, sin and cos columns for each season, and holiday dummies. Its strengths are speed, readable parts and tolerance of missing data. Its weakness is that it ignores recent momentum. So I always compare it with a seasonal naive [[baseline]] and with ARIMA or boosted trees in a backtest.

**Red flags:** Thinking Prophet is a neural network. Saying Fourier terms are "extra data". Not backtesting. Treating the holiday effect as fixed forever.

## Real world

- Sean Taylor and Benjamin Letham from Facebook published the Prophet method in the paper "Forecasting at Scale" (2017/2018). The goal was to give analysts an easy tool for business series with strong seasons and holidays.
- Prophet has also been criticised. In several benchmark studies, simpler or better-tuned models match or beat it, which is a reason to always compare it with baselines.

## Key points

- A series can be modelled as trend + season + holidays, and fitted by linear regression.
- Fourier terms sin(2πkt/P), cos(2πkt/P) give smooth seasons. K sets the detail. Each harmonic needs 2 columns.
- Changepoint columns max(0, t − c) bend the trend. Holiday dummies give event effects.
- Features depend only on dates, so future features are known and there is no recursion.
- Compare with seasonal naive. Prophet is this idea with extra regularisation.
