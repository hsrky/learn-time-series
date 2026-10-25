---
id: s11-02-prophet-at-facebook
title: Prophet at Facebook: a decomposable model
minutes: 25
level: intermediate
goals: [Write the Prophet model as trend plus seasonality plus holidays, Explain changepoints and Fourier terms, Describe the analyst-in-the-loop idea and the main criticism]
prereqs: [s11-01-m-competitions]
tags: [prophet, trend, changepoints, fourier, case-study]
skills: [case-studies, trend-seasonality]
---

## Warm-up

```check
{"q": "Why can averaging two different forecasts help?", "type": "single",
 "options": ["It always gives the true value", "Their errors partly cancel", "It reduces the data size"],
 "answer": 1,
 "why": ["Not always; it only reduces error on average.", "Correct.", "Data size is unchanged."]}
```

```check
{"q": "OWA below 1 means...", "type": "single",
 "options": ["Worse than Naive2", "Better than Naive2", "Equal to a perfect forecast"],
 "answer": 1,
 "why": ["That would be above 1.", "Correct.", "A perfect forecast has OWA 0."]}
```

## Why it matters

Around 2017 Facebook (now Meta) had many teams that needed forecasts: for server capacity, for events, for goals. There were few forecasting experts and many analysts. Sean Taylor and Ben Letham published the paper "Forecasting at Scale". They released **[[Prophet]]** as open source in Python and R. The idea was a model that is easy to use and handles messy business data. Its settings can be understood by a non-expert. Prophet became one of the most used forecasting tools, and also one of the most debated.

## The model: three parts added together

**y(t) = g(t) + s(t) + h(t) + ε(t)**

- `g(t)` = **trend**: growth over time. Either a piecewise linear line or a logistic curve that saturates at a **capacity**.
- `s(t)` = **seasonality**: repeating patterns, such as week and year.
- `h(t)` = **holidays and events**: effects on specific days.
- `ε(t)` = error that the model does not explain.

This is a **decomposable model**: you can plot and judge each part alone. That is why analysts like it.

```check
{"q": "In the Prophet model, which part describes the effect of Christmas Day?", "type": "single",
 "options": ["g(t)", "s(t)", "h(t)", "ε(t)"],
 "answer": 2,
 "why": ["g is the trend.", "s is the regular weekly or yearly cycle.", "Correct: h(t) holds holiday and event effects.", "ε is the unexplained noise."]}
```

## Trend with changepoints

Real growth rates change: a product launches, a market matures. Prophet allows the trend slope to change at **[[changepoint|changepoints]]**.

By default it puts 25 candidate changepoints evenly in the first 80% of the history. It uses a prior that keeps most slope changes near zero. The model picks only the changepoints it needs. A tuning setting, `changepoint_prior_scale`, controls how flexible the trend is: higher means more flexible and more risk of overfitting.

In math, with changepoints `c_1 … c_k`, the trend is **g(t) = a + b·t + Σ d_j · max(0, t − c_j)**. Here `d_j` is the change of slope at `c_j`. You will build this in the practice problem.

```chart
{"title": "A trend whose slope changes twice (plus a weekly cycle)", "x": "day", "height": 230, "series": [{"name": "data", "y": [9.0, 11.6, 14.2, 14.2, 13.3, 11.2, 11.8, 14.7, 19.6, 22.1, 19.6, 16.0, 15.5, 20.0, 21.4, 22.3, 25.6, 23.5, 22.3, 21.7, 22.8, 27.5, 29.9, 30.6, 31.0, 29.7, 25.9, 28.9, 31.2, 35.3, 35.4, 36.1, 34.3, 33.1, 33.6, 37.5, 39.8, 40.9, 42.0, 38.6, 40.5, 40.7, 40.0, 45.3, 44.4, 44.3, 42.0, 38.1, 41.0, 43.5, 47.5, 45.7, 46.6, 42.0, 41.5, 41.6, 46.9, 48.4, 51.4, 47.9, 45.7, 44.3, 43.3, 46.5, 50.8, 49.4, 48.7, 46.1, 45.4, 45.0, 47.8, 50.8, 51.4, 48.9, 48.6, 44.5, 46.2, 49.5, 55.5, 55.5, 54.1, 52.3, 53.6, 53.4, 56.5, 62.1, 61.5, 61.9, 60.7, 59.5, 61.6, 66.6, 67.7, 68.4, 67.1, 67.5, 66.7, 69.0, 71.4, 74.8]}, {"name": "trend only", "y": [10.0, 10.8, 11.6, 12.4, 13.2, 14.0, 14.8, 15.6, 16.4, 17.2, 18.0, 18.8, 19.6, 20.4, 21.2, 22.0, 22.8, 23.6, 24.4, 25.2, 26.0, 26.8, 27.6, 28.4, 29.2, 30.0, 30.8, 31.6, 32.4, 33.2, 34.0, 34.8, 35.6, 36.4, 37.2, 38.0, 38.8, 39.6, 40.4, 41.2, 42.0, 42.2, 42.4, 42.6, 42.8, 43.0, 43.2, 43.4, 43.6, 43.8, 44.0, 44.2, 44.4, 44.6, 44.8, 45.0, 45.2, 45.4, 45.6, 45.8, 46.0, 46.2, 46.4, 46.6, 46.8, 47.0, 47.2, 47.4, 47.6, 47.8, 48.0, 48.2, 48.4, 48.6, 48.8, 49.0, 50.0, 51.0, 52.0, 53.0, 54.0, 55.0, 56.0, 57.0, 58.0, 59.0, 60.0, 61.0, 62.0, 63.0, 64.0, 65.0, 66.0, 67.0, 68.0, 69.0, 70.0, 71.0, 72.0, 73.0], "dash": true}], "marks": [{"x": 40, "label": "changepoint"}, {"x": 75, "label": "changepoint"}], "caption": "The slope is 0.8 until day 40, then 0.2, then 1.0 after day 75. Prophet can learn such slope changes."}
```

```check
{"q": "A higher changepoint_prior_scale makes the trend...", "type": "single",
 "options": ["Stiffer", "More flexible, with a higher risk of overfitting", "Seasonal", "Constant"],
 "answer": 1,
 "why": ["That would be a lower scale.", "Correct: slope changes are penalised less.", "It does not affect seasonality.", "A constant trend has no changepoints at all."]}
```

## Seasonality with Fourier terms

Prophet models a season of period `P` with a **[[Fourier series]]**, a sum of sine and cosine waves:

**s(t) = Σ_{n=1..N} [ a_n · cos(2π·n·t / P) + b_n · sin(2π·n·t / P) ]**

- `P` = period (7 for weekly in days, 365.25 for yearly).
- `N` = number of wave pairs ("order"). Small N gives a smooth shape; large N gives a flexible shape. Defaults are 3 for weekly and 10 for yearly.
- `a_n`, `b_n` = coefficients that the model learns.

This is just **linear regression** on the columns `cos(...)` and `sin(...)`. It is smooth, works with missing days, and can forecast any future date.

```check
{"q": "A yearly season in daily data uses Fourier order N = 10. How many regression columns does it add?", "type": "numeric",
 "answer": 20, "tol": 0.01,
 "why": "Each order has one cos and one sin column: 2 × 10 = 20."}
```

## Analyst in the loop, and the criticism

The paper describes a loop. The model makes a forecast. A **cheap automatic check** flags bad ones. An analyst adjusts understandable settings (changepoints, holidays, capacity) and tries again. The aim is to use human knowledge where it is valuable.

**Criticism.** Later benchmark studies and many practitioner posts looked at many datasets. They found that Prophet is not more accurate than simple baselines or classical models (ETS, ARIMA). Sometimes it is worse. Reasons often given:

- The trend may be extrapolated too confidently, using the last slope.
- It does not model short-term autocorrelation, so recent errors are not used.
- Default settings may overfit changepoints or seasonality.

A fair summary: Prophet is good for daily business data with strong seasons, holidays, and missing days. Use it when you need an interpretable model fast. **Always compare it with seasonal naive and ETS** before you trust it.

```check
{"q": "A colleague says 'Prophet is always best, so no baseline is needed'. What do you answer?", "type": "single",
 "options": ["Agree, it is from Facebook", "Disagree: benchmarks show it can lose to simple models, so always compare with seasonal naive and ETS", "Use only the default settings", "Remove the holidays"],
 "answer": 1,
 "why": ["The origin of a tool does not prove accuracy.", "Correct.", "Defaults are not a guarantee.", "Holidays are one of its strengths."]}
```

## Worked example

We fit a Prophet-like model by hand. It has a trend line and a weekly Fourier season, all by least squares. We compare it with seasonal naive on 28 days of future data.

```python
import numpy as np

rng = np.random.default_rng(1)
n, h = 365, 28
t = np.arange(n + h, dtype=float)
y = 50 + 0.1 * t + 8 * np.sin(2 * np.pi * t / 7) + 3 * np.cos(2 * np.pi * 2 * t / 7) + rng.normal(0, 2, n + h)
train, test = y[:n], y[n:]

def fourier(t, period, order):
    cols = []
    for k in range(1, order + 1):
        cols += [np.sin(2 * np.pi * k * t / period), np.cos(2 * np.pi * k * t / period)]
    return np.column_stack(cols)

def design(t):
    return np.column_stack([np.ones_like(t), t, fourier(t, 7, 3)])   # intercept, trend, weekly season

coef = np.linalg.lstsq(design(t[:n]), train, rcond=None)[0]
forecast = design(t[n:]) @ coef
snaive = train[-7:].tolist() * 4                                       # last week repeated 4 times

print("model MAE      :", round(float(np.mean(np.abs(test - forecast))), 2))
print("seasonal naive :", round(float(np.mean(np.abs(test - np.array(snaive)))), 2))
# Output:
# model MAE      : 1.8
# seasonal naive : 2.83
```

The decomposable model uses the full history, so its season is less noisy than the single last week. This is the situation where Prophet-style models work well. With a trend that changes often or short memory effects, the result can be the opposite.

## Common mistakes

- Using default settings and never checking the forecast against a baseline.
- Too many changepoints on short noisy data (overfitting).
- Forgetting that the trend is extrapolated with the last slope.
- Using multiplicative seasonality for data that is additive, or the reverse.
- Cross-validating with a random split instead of a rolling origin.

## Interview lens

**Typical question:** "What is Prophet and when would you not use it?"

**Strong answer:** Prophet is a decomposable regression model: piecewise trend with changepoints, Fourier seasonality and holiday effects, fitted with Stan. It is quick to use and interpretable, which fits the analyst-in-the-loop idea, and it handles missing data and holidays well. I would not use it blindly. Studies show it often does not beat ETS, ARIMA or even seasonal naive. It ignores recent autocorrelation, and its trend extrapolation can be too confident. I use it as one candidate, check it with a rolling-origin backtest, and compare against simple baselines.

**Red flags:** "Prophet is the best possible model". Not knowing the three components. Not knowing what a changepoint is.

## Real world

The paper is Taylor and Letham, "Forecasting at Scale", published in The American Statistician in 2018. A preprint appeared in 2017. Prophet is open source and was widely adopted. Several public benchmark posts and papers compared it with classical models and found mixed results. That is why practitioners advise treating it as one tool among several.

## Key points

- Prophet: y(t) = trend + seasonality + holidays + error.
- Trend: piecewise linear or logistic, with changepoints and a prior that limits slope changes.
- Seasonality: Fourier series, which is plain linear regression on sine and cosine columns.
- Analyst-in-the-loop: understandable settings that people can adjust.
- Benchmarks show mixed accuracy. Always compare with simple baselines.
