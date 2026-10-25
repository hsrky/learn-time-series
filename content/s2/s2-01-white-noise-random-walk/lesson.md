---
id: s2-01-white-noise-random-walk
title: White noise and random walk
minutes: 25
level: beginner
goals: [Explain white noise in three conditions, Build a random walk from white noise, Explain why the best random walk forecast is the last value, Explain why forecast uncertainty grows with the horizon]
prereqs: []
tags: [white-noise, random-walk, statistics]
skills: [baseline-first, uncertainty]
---

## Warm-up

Two quick questions from earlier lessons. Do not worry if you are unsure. Trying to remember helps you learn.

```check
{"q": "A series goes up by about 2 units every day. What is this pattern called?", "type": "single",
 "options": ["Trend", "Seasonality", "Noise"],
 "answer": 0,
 "why": ["Correct: a slow, steady movement in one direction is a trend.", "Seasonality repeats at a fixed period, for example every 7 days. This series does not repeat.", "Noise is random and has no steady direction."]}
```

```check
{"q": "The series is 5, 7, 6, 10. What is the first difference?", "type": "single",
 "options": ["2, -1, 4", "5, 2, -1, 4", "12, 13, 16"],
 "answer": 0,
 "why": ["Correct: 7-5=2, 6-7=-1, 10-6=4. The result has one value less than the original.", "The difference series is one value shorter. The first value has no earlier value to subtract.", "These are sums of two neighbours, not differences."]}
```

## Why it matters

Imagine a stock price. Today it is 100. Tomorrow it is 101 or 99, and you cannot know which. A forecaster who says "tomorrow will be the same as today" is often hard to beat. Two simple ideas explain why: [[white noise]] and the [[random walk]]. Every other time series model is built on top of them. Interviewers often ask about them first.

## White noise: pure randomness

**White noise** is a series of random numbers with three properties:

1. The average is zero (or a fixed number).
2. The spread ([[variance]]) is the same at every time.
3. Each value is not related to the other values. There is no [[autocorrelation]].

Example: 0.5, -1.2, 0.3, 0.9, -0.4. You cannot guess the next number from the earlier numbers. The best forecast is just the average, which is 0.

We write white noise as ε(t) (the Greek letter epsilon). ε(t) is often called the **error** or **[[shock]]** at time t.

```chart
{"title": "White noise: it jumps around zero with no pattern", "x": "time", "height": 200,
 "series": [{"name": "white noise", "gen": [["noise", {"sd": 1}]], "n": 120, "seed": 5}],
 "caption": "No trend, no season, and the size of the jumps stays the same."}
```

```check
{"q": "Which series can be white noise?", "type": "single",
 "options": ["1, 2, 3, 4, 5, 6", "0.4, -0.9, 1.1, -0.2, 0.6, -1.3", "10, 12, 10, 12, 10, 12"],
 "answer": 1,
 "why": ["This series has a clear trend. You can guess the next value, so it is not white noise.", "Correct: no visible pattern and the values jump around zero.", "This series repeats every 2 steps. A repeating pattern means the values are related."]}
```

## Random walk: the sum of noise

A **random walk** is a series where each value is the last value plus a new random shock:

y(t) = y(t−1) + ε(t)

- y(t): the value now.
- y(t−1): the value one step before.
- ε(t): white noise, the new random step.

Numbers: start at 10. Shocks are +1, −2, +0.5. The walk is 10, 11, 9, 9.5. The walk is the **cumulative sum** (running total) of the shocks.

A random walk **wanders**. It does not return to a fixed mean. Its trend looks real, but the direction is random. We call such a series [[non-stationary]].

```chart
{"title": "Three random walks from the same recipe", "x": "time", "height": 220,
 "series": [
  {"name": "walk A", "gen": [["randomWalk", {"sd": 1, "start": 0}]], "n": 150, "seed": 1},
  {"name": "walk B", "gen": [["randomWalk", {"sd": 1, "start": 0}]], "n": 150, "seed": 2},
  {"name": "walk C", "gen": [["randomWalk", {"sd": 1, "start": 0}]], "n": 150, "seed": 3}
 ],
 "caption": "Same rules, very different paths. Some look like a trend, but there is none."}
```

```check
{"q": "A random walk is 4, 6, 5, 8. What are the shocks ε(t) for the last three steps?", "type": "single",
 "options": ["2, -1, 3", "6, 5, 8", "4, 2, 3"],
 "answer": 0,
 "why": ["Correct: each shock is the difference between two neighbours: 6-4, 5-6, 8-5.", "These are the values of the walk, not the steps.", "This mixes values and steps. The shock is always the difference of two values."]}
```

## Forecasting a random walk

What is the best forecast of y(t+h), h steps ahead? Future shocks have average zero. So the best guess is the **last value**:

ŷ(t+h) = y(t)

This is the **[[naive forecast]]**. For a random walk with **[[drift]]** δ (a small steady push each step) the forecast is:

ŷ(t+h) = y(t) + h·δ

The **uncertainty** grows. After h steps, h shocks are added. The standard deviation of the error is σ·√h, where σ is the standard deviation of one shock. A 95% [[prediction interval]] is about ± 1.96·σ·√h.

Numbers: σ = 2. At h = 1 the half-width is 3.92. At h = 4 it is 7.84. Four times the steps means only twice the width.

```chart
{"title": "Random walk forecast: flat at the last value, with an interval that widens (sigma = 2)", "x": "steps ahead h", "height": 220,
 "series": [
  {"name": "forecast", "x": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16], "y": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]},
  {"name": "upper 95%", "dash": true, "x": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16], "y": [0.0, 3.92, 5.54, 6.79, 7.84, 8.77, 9.6, 10.37, 11.09, 11.76, 12.4, 13.0, 13.58, 14.13, 14.67, 15.18, 15.68]},
  {"name": "lower 95%", "dash": true, "x": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16], "y": [-0.0, -3.92, -5.54, -6.79, -7.84, -8.77, -9.6, -10.37, -11.09, -11.76, -12.4, -13.0, -13.58, -14.13, -14.67, -15.18, -15.68]}
 ],
 "caption": "The width grows like the square root of h. After 16 steps it is only 4 times wider than after 1 step."}
```

```check
{"q": "The last value of a random walk is 50 and σ = 3. What is the 95% interval half-width for h = 9?", "type": "numeric",
 "answer": 17.64, "tol": 0.05,
 "why": "1.96 * 3 * sqrt(9) = 1.96 * 3 * 3 = 17.64."}
```

## Differencing turns a random walk into white noise

Take the [[differencing|first difference]] of a random walk: y(t) − y(t−1) = ε(t). The result is white noise. This is the main trick of the next lessons. A series that becomes [[stationary]] after differencing once is called **integrated of order 1**, written I(1).

Also the other way around: if a model's errors (the [[residual]]s) look like white noise, the model has caught all the pattern. If the residuals still have a pattern, you can improve the model.

```check
{"q": "You fit a model and the residuals show a clear pattern with autocorrelation. What does it mean?", "type": "single",
 "options": ["The model is perfect.", "The model missed some pattern that can still be used.", "The data is white noise."],
 "answer": 1,
 "why": ["A perfect model leaves residuals that look like white noise, with no pattern.", "Correct: leftover autocorrelation means information is still in the residuals.", "If the data were white noise, there would be no autocorrelation in the residuals either."]}
```

## Worked example

We build a random walk from noise, then take the difference to get the noise back.

```python
import numpy as np

rng = np.random.default_rng(42)          # fixed seed: same numbers every run
eps = rng.normal(0, 1, 500)              # white noise, mean 0, sd 1
walk = np.cumsum(eps)                    # random walk = running total of shocks

# 1) The noise has mean ~0 and sd ~1
print("noise mean:", round(eps.mean(), 3), "sd:", round(eps.std(), 3))

# 2) Lag-1 correlation: how much does a value predict the next one?
def lag1_corr(x):
    return np.corrcoef(x[:-1], x[1:])[0, 1]

print("noise lag-1 corr:", round(lag1_corr(eps), 3))   # near 0
print("walk  lag-1 corr:", round(lag1_corr(walk), 3))  # near 1

# 3) Differencing the walk returns the noise (except the first value)
back = np.diff(walk)
print("diff equals noise[1:]:", np.allclose(back, eps[1:]))

# 4) Forecast interval of the walk, 1 and 16 steps ahead
sigma = back.std()
for h in (1, 16):
    print("h =", h, "half-width:", round(1.96 * sigma * np.sqrt(h), 2))
# Output:
# noise mean: -0.013 sd: 0.959
# noise lag-1 corr: 0.099
# walk  lag-1 corr: 0.978
# diff equals noise[1:]: True
# h = 1 half-width: 1.88
# h = 16 half-width: 7.53
```

## Common mistakes

- Seeing a trend in a random walk and fitting a straight line. The "trend" is random and will not continue.
- Thinking white noise must be Gaussian (normal). Only the three properties matter.
- Forgetting that the interval of a random walk grows with the [[horizon]]. A flat band is wrong.
- Calling the series white noise after a quick look. Check the [[ACF]] (next lessons).

## Interview lens

**Typical question:** "What is a random walk, and how do you forecast it?"

**Strong answer:** A random walk is the running sum of white noise, so y(t) = y(t−1) + ε(t). It is not stationary, because its variance grows with time. The best point forecast at any horizon is the last observed value, because future shocks have mean zero. The forecast uncertainty grows like σ√h. If you add a constant drift, the forecast is a straight line from the last value. I would always compare any complex model with this naive forecast first.

**Red flags:** Saying a random walk "has a trend you can extrapolate". Saying the interval stays constant. Mixing up white noise (stationary) and random walk (not stationary).

## Real world

- The idea that price changes are hard to predict is old in finance. It is often called the random walk hypothesis. Daily stock prices are often modelled as close to a random walk.
- In forecasting competitions, the plain "naive" forecast is a standard benchmark that every new method must beat.

## Key points

- White noise: zero mean, constant spread, no autocorrelation. Nothing to forecast but the mean.
- Random walk: y(t) = y(t−1) + ε(t). It is the running sum of white noise and it is non-stationary.
- Best forecast of a random walk: the last value (plus h·drift if there is a drift).
- Interval width grows like σ·√h.
- The first difference of a random walk is white noise. Residuals of a good model look like white noise.
