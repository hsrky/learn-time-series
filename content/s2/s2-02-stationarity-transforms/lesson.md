---
id: s2-02-stationarity-transforms
title: Stationarity and transforms
minutes: 30
level: beginner
goals: [Define a stationary series, Use log and Box-Cox to stabilise the spread, Use differencing and seasonal differencing to remove trend and season, Undo a transform to get forecasts back to the original scale]
prereqs: [s2-01-white-noise-random-walk]
tags: [stationarity, log, box-cox, differencing]
skills: [from-scratch]
---

## Warm-up

```check
{"q": "What do you get if you take the first difference of a random walk?", "type": "single",
 "options": ["White noise", "A straight line", "Another random walk with twice the spread"],
 "answer": 0,
 "why": ["Correct: y(t) - y(t-1) = the shock, and shocks are white noise.", "A straight line would need a constant step, but the steps are random.", "The steps are the shocks themselves, so no new walk appears."]}
```

```check
{"q": "The best forecast of a random walk without drift, 10 steps ahead, is...", "type": "single",
 "options": ["The average of all past values", "The last value", "Zero"],
 "answer": 1,
 "why": ["The average ignores where the walk is now.", "Correct: future shocks have mean zero, so the last value is the best guess.", "Only white noise has mean zero. A walk can be far from zero."]}
```

## Why it matters

Most classical models learn rules from the past and use them in the future. This only works if the rules do not change. A trend that grows or a spread that doubles breaks the rules. So the first step of many projects is to make the series **stable**. The word for stable is [[stationary]]. In this lesson you learn four tools: log, Box-Cox, [[differencing]] and [[seasonal difference|seasonal differencing]].

## What stationary means

A series is **stationary** if its statistical behaviour does not depend on the time you look at. Simply:

1. The **mean** is constant (no trend).
2. The **[[variance]]** is constant (the spread is stable).
3. The **[[autocorrelation]]** depends only on the distance between two points, not on where they are.

Stationary examples: [[white noise]]; daily temperature **changes**. Not stationary: a [[random walk]]; sales with growth; a series with a yearly season. A season changes the mean in a repeating way, so the series is not stationary.

```chart
{"title": "Stationary series, and the same series with a trend added", "x": "time", "height": 220,
 "series": [
  {"name": "stationary (AR 0.6)", "gen": [["ar1", {"phi": 0.6, "sd": 1}]], "n": 150, "seed": 4},
  {"name": "same + trend (not stationary)", "gen": [["ar1", {"phi": 0.6, "sd": 1}], ["trend", {"start": 0, "slope": 0.08}]], "n": 150, "seed": 4}
 ],
 "caption": "The first series keeps returning to the same level. The second one moves away."}
```

```check
{"q": "Which series is stationary?", "type": "single",
 "options": ["Monthly airline passengers 1949-1960 (grow and have a yearly season)", "Daily random noise around 0 with a stable spread", "A random walk"],
 "answer": 1,
 "why": ["It has trend and seasonality, so the mean changes over time.", "Correct: constant mean, constant spread, no change in behaviour.", "A random walk wanders. Its variance grows with time."]}
```

## Log transform: stabilise the spread

Sometimes the spread grows together with the [[level]]. Example: sales of 100 vary by ±10. Sales of 1000 vary by ±100. This is a **multiplicative** pattern: effects are percentages.

The **log** turns multiplication into addition: log(a·b) = log(a) + log(b). A constant 10% change becomes a constant step in log space.

Numbers: 100, 110, 121 (each +10%). Natural logs: 4.605, 4.700, 4.796. The steps are both 0.095. Growth is now linear.

Use log only for **positive** values. For values with zeros, use log(1 + y).

```chart
{"title": "Exponential growth: the log makes it a straight line", "x": "time", "height": 200,
 "series": [
  {"name": "sales (original)", "gen": [["exp", {"start": 100, "rate": 0.03}]], "n": 80},
  {"name": "log(sales) x 20 (shifted for the chart)", "gen": [["trend", {"start": 0, "slope": 0.6}]], "n": 80, "dash": true}
 ],
 "caption": "The curve grows faster and faster. In log space it is a straight line."}
```

```check
{"q": "A series grows 5% every month and its spread grows too. Which transform helps first?", "type": "single",
 "options": ["Log", "First difference only", "Subtract the mean"],
 "answer": 0,
 "why": ["Correct: a constant percentage growth becomes a constant step, and the spread becomes stable.", "A difference of raw values still has a growing spread.", "Subtracting a constant does not change the shape or the spread."]}
```

## Box-Cox: a family of power transforms

[[Box-Cox]] is a family of transforms with one number λ (lambda):

w(t) = (y(t)^λ − 1) / λ   if λ ≠ 0
w(t) = ln y(t)            if λ = 0

- y(t): the original value (must be > 0).
- λ: the power.
  - λ = 1 means almost no change.
  - λ = 0.5 is like a square root.
  - λ = 0 is the log.
- w(t): the transformed value.

Numbers: y = 9 and λ = 0.5. y^0.5 = 3. w = (3 − 1) / 0.5 = 4.

How to choose λ: try values until the seasonal swings look the same size over time. Or use a library: `scipy.stats.boxcox` finds λ by [[maximum likelihood]]. To go back: y = (λ·w + 1)^(1/λ), or exp(w) when λ = 0.

```check
{"q": "Box-Cox with lambda = 2 is applied to y = 3. What is w?", "type": "numeric",
 "answer": 4, "tol": 0.001,
 "why": "(3^2 - 1) / 2 = (9 - 1) / 2 = 4."}
```

## Differencing: remove the trend

The **first difference** is y(t) − y(t−1). It measures the change, not the level. Differencing once removes a linear trend and also fixes a random walk. If the differenced series still has a trend, difference again (d = 2). Rarely do you need more than 2.

Numbers: 10, 13, 16, 19 has a linear trend. The differences are 3, 3, 3. Now the mean is constant.

**Warning:** do not over-difference. White noise differenced once becomes a more jagged series with negative autocorrelation. If the series is already stationary, stop.

```widget
{"name": "differencing", "params": {}}
```

```check
{"q": "A series is white noise. You difference it once. What happens?", "type": "single",
 "options": ["Nothing changes", "It gets a new negative autocorrelation at lag 1 (over-differencing)", "It becomes a random walk"],
 "answer": 1,
 "why": ["The variance doubles and a pattern appears, so it does change.", "Correct: e(t) - e(t-1) shares the term e(t-1) with its neighbour, and the sign flips. That is over-differencing.", "A random walk comes from summing, not differencing."]}
```

## Seasonal differencing: remove the season

A **seasonal difference** subtracts the value one full season earlier: y(t) − y(t−m). Here m is the **[[season length]]**. Use m = 7 for daily data with a weekly pattern. Use m = 12 for monthly data with a yearly pattern.

Numbers, m = 4: 10, 20, 30, 40, 12, 22, 32, 42. Differences with [[lag]] 4: 2, 2, 2, 2. The repeating shape is gone. Only the small growth stays.

The first m values are lost. If both trend and season exist, apply the **seasonal difference first**, then the ordinary difference if needed.

```check
{"q": "Monthly data has a yearly season. Which lag gives the seasonal difference?", "type": "single",
 "options": ["1", "7", "12"],
 "answer": 2,
 "why": ["Lag 1 is the ordinary difference. It removes trend, not season.", "Lag 7 fits daily data with a weekly pattern.", "Correct: one season is 12 months, so compare each month with the same month last year."]}
```

## Getting back to the original scale

A model for the transformed series gives forecasts on the transformed scale. You must undo each step in **reverse order**.

1. Undo differencing: add the forecast change to the last known value (a running total, `cumsum`). For a seasonal difference add the value m steps earlier.
2. Undo Box-Cox or log with the inverse formula.

Always report forecasts and errors on the original scale, because that is what the business reads.

## Worked example

We create a series with growth, a weekly season and a growing spread. We measure the spread of each half.

```python
import numpy as np
import pandas as pd

rng = np.random.default_rng(0)
t = np.arange(140)
# Multiplicative series: growth x weekly season x small random factor
y = np.exp(0.02 * t) * (10 + 2 * np.sin(2 * np.pi * t / 7)) * np.exp(rng.normal(0, 0.02, 140))
s = pd.Series(y, index=pd.date_range("2024-01-01", periods=140, freq="D"))

def report(name, x):
    x = x.dropna()
    half = len(x) // 2
    print(f"{name:<14} mean 1st/2nd half: {x[:half].mean():7.3f} {x[half:].mean():7.3f}"
          f"   sd 1st/2nd half: {x[:half].std():6.3f} {x[half:].std():6.3f}")

report("raw", s)
report("log", np.log(s))
report("log + diff(7)", np.log(s).diff(7))       # seasonal difference of the log

# Undo: the last 7 log values + a fake forecast of the seasonal difference
w = np.log(s).diff(7)
last_log = np.log(s).iloc[-7:]                    # one full season of history
fake_next = last_log.values + w.iloc[-7:].values  # y(t) = y(t-7) + diff
print("back on original scale:", np.round(np.exp(fake_next[:3]), 2))
# Output:
# raw            mean 1st/2nd half:  21.564  87.399   sd 1st/2nd half:  9.028 36.760
# log            mean 1st/2nd half:   2.984   4.384   sd 1st/2nd half:  0.424  0.423
# log + diff(7)  mean 1st/2nd half:   0.140   0.140   sd 1st/2nd half:  0.028  0.029
# back on original scale: [178.38 192.89 215.67]
```

## Common mistakes

- Taking the log of zero or negative values. Add a small constant or use log(1 + y) for zeros.
- Differencing too many times. Stop when the plot looks stable. Check the [[ACF]] (next lesson).
- Forgetting to undo the transform before computing the error. Errors on a log scale are not business errors.
- Using the season length from the wrong data frequency, for example 12 for weekly data.
- Fitting the Box-Cox λ on the full data including the test period. Choose it using the training part only.

## Interview lens

**Typical question:** "Why do we need stationarity, and how do you make a series stationary?"

**Strong answer:** Classical models such as [[ARIMA]] estimate stable relationships from the past. If the mean or variance changes over time, those relationships are not stable. To fix a growing spread I use log or Box-Cox. To remove trend I use first differences. To remove a season I use a seasonal difference with lag m. I check the result with a plot and the ACF, and I avoid over-differencing. At the end I invert the transforms so forecasts are on the original scale.

**Red flags:** Saying "stationary means no trend" only (it also needs stable variance and autocorrelation). Differencing a series that is already stationary. Forgetting to invert the transform. Choosing λ on test data.

## Real world

- The classic textbook example is the monthly international airline passengers series (1949–1960) from Box and Jenkins. It has growth, a yearly season and a growing spread. Taking the log and then differencing is the standard first lesson.
- The Box-Cox family is from a 1964 paper by George Box and David Cox. It is still the default tool for stabilising variance in forecasting libraries.

## Key points

- Stationary: constant mean, constant variance, autocorrelation depends only on the lag.
- Log or Box-Cox stabilise a spread that grows with the level (values must be positive).
- First difference removes a trend. Seasonal difference with lag m removes a season. Do not over-difference.
- Undo transforms in reverse order and measure errors on the original scale.
