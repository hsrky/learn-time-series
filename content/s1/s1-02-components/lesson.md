---
id: s1-02-components
title: Trend, season, cycle and noise
minutes: 25
level: beginner
goals: [Name the four parts of a time series, Tell a season from a cycle, Write the additive and the multiplicative model, Choose between them by looking at a chart]
prereqs: [s1-01-what-is-a-time-series]
tags: [trend, seasonality, cycle, noise, additive, multiplicative]
skills: [baseline-first]
---
## Warm-up

```check
{"q": "Which data type has many shops and many days in one table?", "type": "single",
 "options": ["Panel data", "Cross-sectional data", "An irregular series"], "answer": 0,
 "why": ["Correct. Many things over many moments.", "Cross-sectional has only one moment.", "Days are regular here."]}
```

```check
{"q": "pd.infer_freq(s.index) returns None. What is a likely reason?", "type": "single",
 "options": ["Some dates are missing or steps are unequal", "The series has a trend", "The values are floats"], "answer": 0,
 "why": ["Correct. Without one regular step there is no frequency.", "Trend does not change the index.", "Value types do not matter for the index."]}
```

## Why it matters

An ice cream shop sells more in summer than in winter. Sales also grow slowly every year as the shop becomes known. And each day has some random luck.

These are three different effects mixed in one line. If you can name them, you can describe the data, choose a model, and explain a forecast to a manager.

This lesson gives you the four names: trend, season, cycle, noise.

## The four components

Look at a series and ask four questions.

| Component | Question | Example |
|---|---|---|
| [[trend]] | Does the level go up or down over a long time? | Users of an app grow every year |
| [[seasonality]] | Is there a pattern that repeats with a **fixed** period? | Sales peak every Saturday |
| [[cycle]] | Are there rises and falls with **no fixed** length? | Business booms and recessions |
| [[noise]] | What is left? Random small changes | Luck, measurement errors |

Seasonality has a known length (7 days, 12 months). A cycle does not. Cycles are usually longer than one year and are hard to predict.

```chart
{"title": "Trend + weekly season + noise", "x": "day", "height": 240,
 "series": [
  {"name": "sales", "gen": [["trend", {"slope": 0.5, "start": 10}], ["season", {"period": 7, "amp": 5}], ["noise", {"sd": 1.5}]], "n": 84, "seed": 3},
  {"name": "trend only", "gen": [["trend", {"slope": 0.5, "start": 10}]], "n": 84, "dash": true}
 ],
 "caption": "The dashed line is the trend. The solid line repeats every 7 days (season) and has small random errors (noise)."}
```

```check
{"q": "Electricity use peaks every winter. What is this?", "type": "single",
 "options": ["Seasonality", "A cycle", "Trend"], "answer": 0,
 "why": ["Correct. The pattern repeats with a fixed period of one year.", "A cycle has no fixed length. Winter comes every year.", "Trend is a long-run rise or fall, not a repeat."]}
```

## Trend: a number you can compute

A trend can be a straight line: `y = a + b·t`.

- `t`: the time step (0, 1, 2, ...).
- `b`: the **slope**, the change per step.
- `a`: the **intercept**, the value at t = 0.

Example: weekly users are 100, 110, 125, 135, 150. The line grows 12.5 users per week, so b = 12.5.

You find the best line by [[least squares]]. Choose a and b so that the sum of squared gaps between line and data is smallest. In numpy: `np.polyfit(t, y, 1)`. Or use the closed form:

b = Σ (t − t̄)(y − ȳ) / Σ (t − t̄)²   and   a = ȳ − b · t̄

- t̄ and ȳ: the mean of t and the mean of y.
- Σ: add up over all points.

```python
import numpy as np

y = np.array([100.0, 110.0, 125.0, 135.0, 150.0])
t = np.arange(len(y))                      # 0, 1, 2, 3, 4

b = ((t - t.mean()) * (y - y.mean())).sum() / ((t - t.mean()) ** 2).sum()
a = y.mean() - b * t.mean()
print(round(b, 2), round(a, 2))            # slope and intercept
print(np.polyfit(t, y, 1).round(2))        # numpy gives the same answer
# Output:
# 12.5 99.0
# [12.5 99. ]
```

```check
{"q": "A trend line is y = 50 + 4·t, with t = 0 on day 1. What does it predict at t = 10?", "type": "numeric", "answer": 90, "tol": 0,
 "why": "50 + 4 × 10 = 90."}
```

## Season: a pattern that repeats

The **period** is the number of steps in one repeat. Examples:

- 7 for daily data with a weekly pattern.
- 12 for monthly data with a yearly pattern.
- 24 for hourly data with a daily pattern.

A series can have **several** seasons at once. Hourly electricity use has a daily season (24) and a weekly season (168).

The seasonal part tells how much higher or lower than usual each position in the period is. Example: Saturday is +8 against the weekly level, Tuesday is −5.

```widget
{"name": "components", "params": {}}
```

```check
{"q": "Monthly sales data. How long is the period of a yearly season?", "type": "numeric", "answer": 12, "tol": 0,
 "why": "One year has 12 monthly steps, so the period is 12."}
```

## Additive and multiplicative models

How do the parts combine? Two simple models:

- [[additive model]]: y = trend + season + noise. The size of the season is the same at all levels.
- [[multiplicative model]]: y = trend × season × noise. The season is a **percentage** of the level. When the level grows, the swings grow.

Look at the chart. If the seasonal swings **stay the same size**, use additive. If they **grow with the level**, use multiplicative.

Trick: take the logarithm. `log(a × b) = log(a) + log(b)`. So a multiplicative series becomes additive after `np.log`.

```chart
{"title": "Additive vs multiplicative", "x": "month", "height": 240,
 "series": [
  {"name": "additive: swing stays about 20 wide", "y": [50.0, 56.5, 61.7, 64.5, 64.7, 62.5, 59.0, 55.5, 53.3, 53.5, 56.3, 61.5, 68.0, 74.5, 79.7, 82.5, 82.7, 80.5, 77.0, 73.5, 71.3, 71.5, 74.3, 79.5, 86.0, 92.5, 97.7, 100.5, 100.7, 98.5, 95.0, 91.5, 89.3, 89.5, 92.3, 97.5, 104.0, 110.5, 115.7, 118.5, 118.7, 116.5, 113.0, 109.5, 107.3, 107.5, 110.3, 115.5]},
  {"name": "multiplicative: swing grows with the level", "y": [50.0, 56.7, 62.2, 65.4, 65.7, 63.3, 59.0, 54.5, 51.3, 50.8, 53.7, 59.8, 68.0, 76.5, 83.3, 87.0, 86.8, 83.0, 77.0, 70.7, 66.1, 65.2, 68.6, 76.0, 86.0, 96.3, 104.4, 108.6, 107.9, 102.9, 95.0, 86.9, 81.0, 79.6, 83.5, 92.2, 104.0, 116.0, 125.5, 130.2, 129.1, 122.7, 113.0, 103.1, 95.9, 94.0, 98.4, 108.4], "dash": true}
 ],
 "caption": "Both series have the same trend and season. In the solid line the waves keep their height. In the dashed line each wave is 20% of the level, so the waves grow."}
```

```check
{"q": "Airline passengers: the summer peak is 20% above normal, every year. Passengers grow each year. Which model?", "type": "single",
 "options": ["Multiplicative", "Additive", "Neither"], "answer": 0,
 "why": ["Correct. The swing is a percentage of the level, so it grows with the level.", "An additive swing would stay the same absolute size.", "One of the two fits well."]}
```

## Worked example

Task: build a synthetic monthly series with known parts. Then recover the trend and the monthly season from the data.

```python
import numpy as np

rng = np.random.default_rng(0)
n = 48                                              # 4 years of months
t = np.arange(n)

trend = 100 + 2.0 * t                               # +2 per month
season = np.tile([-8, -6, -2, 0, 3, 6, 9, 8, 4, 0, -5, -9], 4)   # period 12, sums to 0
noise = rng.normal(0, 1.0, n)
y = trend + season + noise                          # additive model

# 1) Estimate the trend line by least squares
b, a = np.polyfit(t, y, 1)
print("slope", round(b, 2), "intercept", round(a, 2))

# 2) Remove the trend, then average each calendar position
detrended = y - (a + b * t)
est_season = detrended.reshape(4, 12).mean(axis=0)  # rows = years, columns = months
print(est_season.round(0).astype(int))
print("true season:", season[:12])
# Output:
# slope 2.03 intercept 99.37
# [-8 -6 -2  0  2  6  9  9  4  0 -5 -9]
# true season: [-8 -6 -2  0  3  6  9  8  4  0 -5 -9]
```

The estimates are close to the true values. The small differences are the noise.

## Common mistakes

- Calling a repeat with no fixed length a season. It is a cycle.
- Using the additive model when the swings grow with the level.
- Forgetting a second season (daily and weekly).
- Fitting a straight trend line to data that bends, then extending it far into the future.
- Thinking noise is useless. It sets the limit of how accurate any forecast can be.

## Interview lens

**Typical question:** "A series has seasonal swings that grow over time. How do you model it?"

**Strong answer:** The swings grow with the level, so the series is multiplicative. I can model it directly with a multiplicative seasonal model, or I take the log. After the log the swings have constant size, so an additive model fits. I forecast in log space and transform back with `exp`. I keep in mind that the back-transform gives a median-like forecast, not the mean.

**Red flags:**
- Not seeing the difference between a cycle and a season.
- Fitting a model before looking at the plot.
- Applying log to values that are zero or negative without a plan.

## Real world

- The classic "airline passengers" series (monthly, 1949–1960, from Box and Jenkins' textbook) is the standard example of trend plus a growing yearly season.
- Retail demand almost always has weekly and yearly seasons. Competitions such as M5 (Walmart) rely on calendar features for this reason.

## Key points

- Four parts: trend (long-run level), seasonality (fixed period), cycle (no fixed period), noise (random rest).
- Additive: y = T + S + N. Multiplicative: y = T × S × N. Log turns one into the other.
- If the swings grow with the level, think multiplicative.
- A straight trend is the least-squares line. A season is the average pattern at each position of the period.
