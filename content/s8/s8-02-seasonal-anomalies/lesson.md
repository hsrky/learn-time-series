---
id: s8-02-seasonal-anomalies
title: Seasonal anomalies: STL and ESD
minutes: 25
level: intermediate
goals: [Remove the season before scoring, Explain the generalized ESD test, Describe S-H-ESD]
prereqs: [s8-01-point-anomalies]
tags: [anomaly, stl, esd]
skills: [anomaly-detection, decomposition]
---
## Warm-up
```check
{"q": "In the robust z-score, which two statistics replace the mean and the standard deviation?", "type": "single", "options": ["Minimum and maximum", "Median and MAD", "Mode and range"], "answer": 1, "why": ["These are very sensitive to outliers.", "Correct: median and MAD.", "The range is very sensitive to outliers."]}
```
```check
{"q": "What is a [[seasonal]] pattern?", "type": "single", "options": ["A pattern that repeats at a fixed period, like every 7 days", "A long upward movement", "Random noise"], "answer": 0, "why": ["Correct: for example, weekends are higher every week.", "That is a trend.", "Noise has no repeating pattern."]}
```

## Why it matters
An online shop sells 500 items on Saturday and 200 on Tuesday. That is normal. But 300 on a Saturday is strange, even though 300 is a common Tuesday value. A plain z-score misses this, because it ignores the weekly pattern. To find **seasonal anomalies** you first remove the pattern, then look at what is left.

## Remove the season first: STL residuals
[[STL]] (Seasonal-Trend decomposition using Loess) splits a series into three parts:

`y(t) = trend(t) + season(t) + residual(t)`

- `trend(t)` = the slow movement
- `season(t)` = the repeating pattern
- `residual(t)` = what is left (the "surprise")

Plan: fit STL, take the **residual**, and run a robust z-score on it. A Saturday of 300 items has a big negative residual, because the model expected 500.

```chart
{"title": "Weekly season + noise + one broken Saturday", "x": "day", "height": 230, "series": [{"name": "orders", "gen": [["const", {"value": 100}], ["season", {"period": 7, "amp": 30}], ["noise", {"sd": 3}], ["spike", {"at": 47, "size": -45}]], "n": 70, "seed": 2}, {"name": "expected", "gen": [["const", {"value": 100}], ["season", {"period": 7, "amp": 30}]], "n": 70, "dash": true}], "marks": [{"x": 47, "label": "anomaly"}], "caption": "The dip at day 47 is inside the normal range of the whole series, but it is far below the expected line."}
```

```check
{"q": "Why do we score the STL residual and not the raw series?", "type": "single", "options": ["The residual has the trend and season removed, so normal repeats are not flagged", "The residual is always normal", "The residual is shorter"], "answer": 0, "why": ["Correct: normal weekly highs and lows become close to zero.", "No. The residual can still have outliers and heavy tails.", "STL residuals have the same length."]}
```

## Generalized ESD and Seasonal Hybrid ESD
The [[ESD]] test (Extreme Studentized Deviate) finds up to **r** outliers without you choosing a threshold by hand. It repeats these steps:

1. Compute `R = max |x − mean| / s` over the remaining points (`s` = sample standard deviation).
2. Remove the most extreme point. Store its R.
3. Repeat r times. Compare each R(i) with a critical value λ(i).

The number of outliers is the **largest i** with `R(i) > λ(i)`.

`λ(i) = (n−i)·t / sqrt((n−i−1+t²)·(n−i+1))`

- `n` = number of points, `i` = step (1…r)
- `t` = the value of the Student t distribution with `n−i−1` degrees of freedom at probability `p = 1 − α / (2·(n−i+1))`
- `α` = the false-alarm level, often 0.05

**Seasonal Hybrid ESD (S-H-ESD)** was published by Twitter engineers (Hochenbaum, Vallis, Kejariwal, 2017) for the open-source AnomalyDetection package. It runs STL, then builds the residual as `y − season − median(y)`. The series median replaces the fitted trend, because the trend can follow the anomalies. The ESD test then uses the median and the MAD instead of the mean and the standard deviation. This makes the method robust to the anomalies it wants to find.

```check
{"q": "What does the ESD test need you to choose?", "type": "single", "options": ["The maximum number of outliers r and the level α", "The exact positions of the outliers", "A window size"], "answer": 0, "why": ["Correct: r is an upper limit, the test decides how many are real.", "It finds the positions for you.", "ESD works on the whole sample; there is no window."]}
```

## Worked example
We build a weekly series, remove the season with STL, and score the residual with median and MAD.

```python
import numpy as np, pandas as pd
from statsmodels.tsa.seasonal import STL

rng = np.random.default_rng(1)
t = np.arange(98)
y = 100 + 30 * np.sin(2 * np.pi * t / 7) + rng.normal(0, 3, 98)
y[50] -= 60                              # a broken day inside the season

s = pd.Series(y, index=pd.date_range("2024-01-01", periods=98, freq="D"))
res = STL(s, period=7, robust=True).fit()     # robust=True lowers the effect of outliers
r = res.resid                                  # what is left after trend and season

med = r.median()
mad = (r - med).abs().median()
score = 0.6745 * (r - med) / mad               # robust z of the residual
# normal days reach about |6|; the broken day is far larger, so we use a cut-off of 10
print(score[score.abs() > 10].round(1))

# Output:
# 2024-02-20   -44.5
# Freq: D, Name: resid, dtype: float64
```

## Common mistakes
- Scoring the raw series when a strong season exists.
- Using the wrong `period` in STL (for hourly data with a daily pattern the period is 24, with a weekly pattern 168).
- Fitting STL on the full series including the test period: that is leakage in a live system. Fit on past data only.
- Setting the ESD limit `r` too small and missing outliers, or α too large and getting false alarms.
- Ignoring that holidays are "anomalies" for the model but are expected by the business.

## Interview lens
**Typical question:** "Traffic has a daily and weekly pattern. How do you find anomalies?"

**Strong answer:** I remove the pattern first, using STL or a seasonal baseline such as "same hour last week". Then I score the residual with a robust measure, for example median and MAD, or the ESD test if I want a statistical limit on the number of outliers. For a live system I fit only on past data and refresh the model regularly. I also keep a list of known events, like holidays, so they do not create alerts.

**Red flags:** applying a global threshold on a seasonal series; not knowing the period; claiming the ESD test needs the number of outliers in advance.

## Real world
- Twitter published the S-H-ESD method and an open-source R package called AnomalyDetection. It was used to find anomalies in metrics such as traffic.
- Rosner's generalized ESD test comes from a 1983 paper in the journal Technometrics. It is also described in the NIST engineering statistics handbook.

## Key points
- A seasonal series needs the pattern removed before scoring: use STL (or "same time last week").
- Score the **residual** with a robust method (median and MAD).
- The generalized ESD test finds up to r outliers and decides how many are real.
- S-H-ESD = STL + (robust) ESD. Fit on past data only in production.
