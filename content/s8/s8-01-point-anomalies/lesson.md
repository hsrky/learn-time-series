---
id: s8-01-point-anomalies
title: Point anomalies: z-score and robust z
minutes: 25
level: beginner
goals: [Compute a z-score and a robust z-score, Explain why outliers hide themselves, Build a rolling score with no leakage]
prereqs: []
tags: [anomaly, z-score, mad]
skills: [anomaly-detection]
---
## Warm-up
```check
{"q": "What does the mean of a list of numbers tell you?", "type": "single", "options": ["The middle value after sorting", "The sum divided by the count", "The biggest value"], "answer": 1, "why": ["That is the median, not the mean.", "Correct: add all values, then divide by how many there are.", "That is the maximum."]}
```
```check
{"q": "Which is the best description of a rolling window?", "type": "single", "options": ["All data from the start of the series", "The last k values, moving forward one step at a time", "Only the first k values"], "answer": 1, "why": ["That is an expanding window.", "Correct: the window slides, and always holds the k newest points.", "A rolling window moves; it does not stay at the start."]}
```

## Why it matters
A bank sees 40 card payments per hour. Suddenly one hour has 4,000. Is it a sale, or is it fraud? An **anomaly** (a point that does not fit the normal pattern) is often the first sign of a problem. The simplest tool to find one is the [[z-score]]. It is cheap, fast, and a strong first baseline in any interview.

## The z-score: how far from normal?
Take five daily sales numbers: 10, 12, 11, 13, 40. The mean is 17.2. The [[standard deviation]] is about 11.4. For the last day:

`z = (40 − 17.2) / 11.4 ≈ 2.0`

The formula:

`z(t) = (x(t) − μ) / σ`

- `x(t)` = the value at time t
- `μ` (mu) = the mean of the data
- `σ` (sigma) = the standard deviation
- `z` = how many standard deviations the value is from the mean

A common rule: flag the point if `|z| > 3`. For a bell-shaped (normal) distribution, only about 0.3% of points are that far out.

```widget
{"name": "anomaly-zscore", "params": {"threshold": 3}}
```

Look at the example. The 40 is a big [[outlier]], but its z-score is only 2.0. The outlier itself made the mean and the spread bigger. This is called **masking**.

```check
{"q": "Why can a very large outlier hide itself when you use the plain z-score?", "type": "single", "options": ["It makes the mean and standard deviation larger", "It makes the median smaller", "It changes the sampling frequency"], "answer": 0, "why": ["Correct: the outlier is part of the data used to compute μ and σ, so the z-score shrinks.", "The plain z-score does not use the median.", "Frequency does not change when one value is large."]}
```

## Robust z-score: median and MAD
A **robust** method does not break easily when outliers are present. Use the [[median]] instead of the mean. Use the [[MAD]] (median absolute deviation) instead of the standard deviation.

For 10, 12, 11, 13, 40: the median is 12. The absolute distances from 12 are 2, 0, 1, 1, 28. The median of those is **MAD = 1**.

`robust z(t) = 0.6745 · (x(t) − median) / MAD`

- `0.6745` makes MAD comparable to the standard deviation for normal data
- A common cut-off (Iglewicz and Hoaglin) is `|robust z| > 3.5`

For 40: `0.6745 · 28 / 1 = 18.9`. Now the [[anomaly]] is very clear.

```chart
{"title": "One spike: the mean and the median react differently", "x": "day", "height": 220, "series": [{"name": "sales", "gen": [["const", {"value": 50}], ["noise", {"sd": 2}], ["spike", {"at": 30, "size": 40}]], "n": 60, "seed": 4}, {"name": "normal level", "gen": [["const", {"value": 50}]], "n": 60, "dash": true}], "marks": [{"x": 30, "label": "anomaly"}], "caption": "A single spike pulls the mean up a little, but the median stays at the normal level."}
```

```check
{"q": "Values: 2, 4, 4, 5, 100. The median is 4 and MAD is 1. What is the robust z of 100 (use 0.6745, round to 1 decimal)?", "type": "numeric", "answer": 64.8, "tol": 0.2, "why": "(100 − 4) = 96. 0.6745 × 96 / 1 = 64.75, which is about 64.8."}
```

## Rolling z-score without leakage
Time series change over time, so one global mean is wrong. Use a **[[rolling window]]**: compare each point with the last `k` points.

**Leakage** means using information from the future (or from the point itself) to judge a point. Two rules:

1. The window must hold only **past** values: positions `t−k … t−1`.
2. Do **not** include `x(t)` in its own window. If you do, the point hides itself, like masking above.

In pandas: `s.rolling(k).mean().shift(1)`. The `shift(1)` moves the result one step, so row t uses the window that ended at t−1.

```check
{"q": "You compute z(t) with a window that includes x(t) itself. What is the main risk?", "type": "single", "options": ["Anomalies are partly hidden, so you miss some", "The code runs slower", "The index becomes unsorted"], "answer": 0, "why": ["Correct: the point raises the mean and spread of its own window, so its z-score is smaller.", "Speed is not the issue here; the result is wrong.", "The index order does not change."]}
```

## Worked example
We flag a spike in a series with a slow trend. The window holds the 10 previous points.

```python
import numpy as np, pandas as pd

rng = np.random.default_rng(0)
s = pd.Series(100 + 0.5 * np.arange(60) + rng.normal(0, 1, 60))
s.iloc[40] += 15                       # put one spike at position 40

k = 10
past = s.shift(1)                      # past values only: no leakage
mean = past.rolling(k).mean()          # mean of the last k past values
std = past.rolling(k).std(ddof=0)      # standard deviation of the same window
z = (s - mean) / std                   # z-score of each point

print(z[z.abs() > 3].round(2))         # points with |z| > 3

# Output:
# 40    8.35
# dtype: float64
```

Note: a trend makes the rolling mean lag behind. That is why we use a short window, or first remove the trend (for example with differences).

## Common mistakes
- Using the global mean and standard deviation on a series with trend or season.
- Letting the point be inside its own window (leakage / masking).
- Dividing by zero when the window is flat (standard deviation = 0). Always handle it.
- Using `|z| > 3` for heavy-tailed data and getting many false alarms.
- Forgetting that the first `k` points have no score.

## Interview lens
**Typical question:** "How would you detect anomalies in a daily sales series?"

**Strong answer:** Start with a rolling robust z-score as a baseline. Use only past data in the window, so the method also works online. Use median and MAD so past outliers do not inflate the spread. Choose the window to match the data, for example 7 or 28 days. Choose the [[threshold]] from the cost of false alarms, not only from the "3 sigma" rule. If the series has a season, remove it first (next lessons).

**Red flags:** using one global mean on a trending series; not mentioning leakage; saying "3 sigma" without checking for a roughly normal shape.

## Real world
- The "modified z-score" with 0.6745 and the 3.5 cut-off comes from Iglewicz and Hoaglin's 1993 handbook on outlier detection.
- Control charts in factories (Shewhart charts) use the same idea of limits at 3 standard deviations around a mean.

## Key points
- z-score = (value − mean) / standard deviation. Flag when `|z|` is large (often > 3).
- Outliers inflate the mean and spread, so use the **robust z** (median and MAD) instead.
- For time series use a **rolling** window of past values only, and never include the current point.
- Always handle a window with zero spread.
