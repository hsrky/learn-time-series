---
id: s2-05-spurious-regression-cross-correlation
title: Spurious regression and cross-correlation
minutes: 30
level: intermediate
goals: [Explain why two unrelated trending series can look strongly related, Avoid the trap by differencing before you correlate, Compute and read the cross-correlation to find which series leads, Know the sign convention for lead and lag]
prereqs: [s2-04-unit-root-adf-kpss]
tags: [spurious-regression, cross-correlation, lead-lag]
skills: [from-scratch, communication]
---

## Warm-up

```check
{"q": "ADF p-value is 0.80 and KPSS p-value is 0.01. What is the best next step?", "type": "single",
 "options": ["Difference the series", "Use the series as it is", "Collect no more data and stop"],
 "answer": 0,
 "why": ["Correct: both tests point to a unit root.", "The tests say the series is not stationary.", "The result is clear enough to act: make it stationary."]}
```

```check
{"q": "The ACF band for n = 400 points is about...", "type": "single",
 "options": ["±0.098", "±0.5", "±1.96"],
 "answer": 0,
 "why": ["Correct: 1.96 / sqrt(400) = 0.098.", "0.5 is too large for 400 points.", "1.96 is the z-value, not the band. You must divide by the square root of n."]}
```

## Why it matters

A famous joke: ice cream sales and drowning accidents both go up in summer, so ice cream "causes" drowning. The real reason is a third thing: warm weather. In time series it is even worse. Two series with **no link at all** can show a strong correlation just because both wander. If you do not know this, you may build a model on a false signal. Interviewers like to check this.

## Spurious regression

Take two **independent** [[random walk|random walks]]. They share nothing. Yet when you regress one on the other, you often get a high R² (for example 0.7) and a "[[significant]]" slope. This is a **[[spurious regression]]**.

Why? A random walk drifts. Over a window, both series go up or down by chance, and the numbers make a pattern. The usual statistics assume [[stationary]] data, so the [[p-value|p-values]] are far too small.

Warning signs:

- High R² and a very low [[Durbin-Watson]] statistic (close to 0). A simple rule: if R² is larger than Durbin-Watson, be suspicious.
- The [[residual|residuals]] of the regression have a strong [[autocorrelation]].

```chart
{"title": "Two independent random walks: they look related by chance", "x": "time", "height": 220,
 "series": [
  {"name": "walk X", "gen": [["randomWalk", {"sd": 1, "start": 0}]], "n": 150, "seed": 21},
  {"name": "walk Y", "gen": [["randomWalk", {"sd": 1, "start": 0}]], "n": 150, "seed": 22}
 ],
 "caption": "Nothing links these two series. Their levels can still correlate strongly."}
```

```check
{"q": "You regress sales on website visits (both trend upward) and get R² = 0.95 with a Durbin-Watson of 0.2. What is the right reaction?", "type": "single",
 "options": ["Suspect a spurious regression and test again on differences", "Celebrate: the model is excellent", "Add more variables to raise R² further"],
 "answer": 0,
 "why": ["Correct: high R² plus a very low Durbin-Watson is the classic warning sign.", "A high R² on trending data says little about a real link.", "More variables on non-stationary data can make the problem worse."]}
```

## How to avoid it

1. **Plot** both series. Look for trends.
2. **Make them stationary**, usually by taking [[differencing|first differences]] (or growth rates).
3. Correlate or regress the **changes**, not the levels.
4. If the levels truly move together in the long run, they may be **[[cointegration|cointegrated]]**. This is an advanced topic: the combination of the two series is stationary. Then a special model (error correction) is used.

Numbers: two random walks can have a correlation of levels 0.8. The correlation of their first differences is close to 0, for example 0.02. The second number is the honest one.

```check
{"q": "Series A and B are independent random walks. Which correlation is most likely close to zero?", "type": "single",
 "options": ["Correlation of the first differences", "Correlation of the levels", "Both are always close to zero"],
 "answer": 0,
 "why": ["Correct: the differences are independent white noise series, so their correlation is near 0.", "Levels of independent walks often show a large correlation by chance.", "Levels are the problem. They can correlate strongly."]}
```

## Cross-correlation: who leads?

Sometimes one series really does move first. Example: advertising spend today raises sales 3 days later. The **[[cross-correlation]]** between x and y at [[lag]] k is the correlation between x(t) and y(t+k).

- k > 0: x(t) is paired with a **later** value of y. A peak at k = 3 means **x leads y by 3 steps**.
- k < 0: y leads x.
- k = 0: they move at the same time.

Use the same band as [[ACF]]: ±1.96/√n.

```chart
{"title": "Cross-correlation of x and y at lags 0 to 7: one clear peak at lag 3", "x": "lag k", "height": 200,
 "series": [{"name": "corr(x(t), y(t+k))", "kind": "bar", "x": [0,1,2,3,4,5,6,7], "y": [0.0, 0.17, 0.17, 0.96, 0.15, 0.2, 0.04, 0.12]}],
 "caption": "Here y(t) is x(t-3) plus a little noise. The peak at lag 3 shows x leads y by 3 steps."}
```

```check
{"q": "The cross-correlation corr(x(t), y(t+k)) peaks at k = -2. Who leads?", "type": "single",
 "options": ["y leads x by 2 steps", "x leads y by 2 steps", "They move at the same time"],
 "answer": 0,
 "why": ["Correct: a negative lag means y values at earlier times match x. So y comes first.", "That would need a peak at k = +2.", "Same time means a peak at k = 0."]}
```

## Pre-whitening and good practice

Two trending series also create fake peaks in the cross-correlation. So:

1. Make both series stationary first (differences).
2. Remove autocorrelation if it is strong (fit a small AR model to x, apply the same filter to both, correlate the residuals). This is called **[[pre-whitening]]**.
3. Search lags in a limited range that makes business sense (for example 0 to 14 days).
4. A lead-lag link is **not proof of cause**. It only says the past of one series helps to guess the other. The next lesson is about this.

## Worked example

We repeat an experiment 200 times with two independent random walks. Then we find the lead of a series that really leads.

```python
import numpy as np

rng = np.random.default_rng(0)

# Part 1: independent random walks, correlation of levels vs differences
big_levels = big_diffs = 0
for _ in range(200):
    a = np.cumsum(rng.normal(size=200))
    b = np.cumsum(rng.normal(size=200))
    big_levels += abs(np.corrcoef(a, b)[0, 1]) > 0.5
    big_diffs += abs(np.corrcoef(np.diff(a), np.diff(b))[0, 1]) > 0.5
print("share with |corr| > 0.5, levels:     ", big_levels / 200)
print("share with |corr| > 0.5, differences:", big_diffs / 200)

# Part 2: lead-lag. y follows x with a delay of 3 steps
def cross_corr(x, y, k):
    # correlation between x(t) and y(t+k); k > 0 means x leads y
    if k >= 0:
        return np.corrcoef(x[:len(x) - k], y[k:])[0, 1]
    return np.corrcoef(x[-k:], y[:len(y) + k])[0, 1]

x = rng.normal(size=300)
y = np.roll(x, 3) + rng.normal(0, 0.5, 300)     # y(t) = x(t-3) + noise
y[:3] = rng.normal(size=3)                      # remove the wrapped-around values
lags = range(-6, 7)
values = [cross_corr(x, y, k) for k in lags]
best = list(lags)[int(np.argmax(np.abs(values)))]
print("best lag:", best, "corr:", round(max(values), 2))
print("band:", round(1.96 / np.sqrt(300), 3))
# Output:
# share with |corr| > 0.5, levels:      0.37
# share with |corr| > 0.5, differences: 0.0
# best lag: 3 corr: 0.9
# band: 0.113
```

## Common mistakes

- Correlating levels of trending series and reporting the number as a result.
- Reading a cross-correlation peak as proof of cause.
- Mixing up the sign convention. Always say which series is first in your function.
- Testing many lags and reporting the best one without a correction. With 30 lags, a few will be "significant" by chance.
- Forgetting to check for a common season, which gives peaks at multiples of the [[season length]].

## Interview lens

**Typical question:** "Two metrics both grow over time and have a correlation of 0.9. Does one drive the other?"

**Strong answer:** Not necessarily. Two trending or random-walk series can show a high correlation by chance. This is the spurious regression problem. I would first test for stationarity, then difference both series and correlate the changes. Then I would use the cross-correlation to see if one leads the other, and at which lag. Even then it shows predictive order, not cause, so I would use a Granger test or an experiment to learn more.

**Red flags:** Reporting R² on trending levels as evidence. Saying "correlation 0.9 means cause". Not knowing that differencing is the first fix.

## Real world

- Clive Granger and Paul Newbold published "Spurious regressions in econometrics" in 1974. They showed with simulations that independent random walks often give a high R² in regression. This paper changed how economists treat trending data.
- The Granger-Newbold idea is one reason modern forecasting libraries and courses start with stationarity checks.

## Key points

- Independent trending series can show a high correlation of levels. This is spurious regression.
- Warning signs: high R², low Durbin-Watson, autocorrelated residuals. Fix: difference first.
- Cross-correlation at lag k pairs x(t) with y(t+k). A peak at k > 0 means x leads y.
- Make series stationary (and pre-whiten) before you search for lags.
- A lead-lag pattern shows prediction order, not cause.
