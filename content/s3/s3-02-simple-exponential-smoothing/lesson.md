---
id: s3-02-simple-exponential-smoothing
title: Simple exponential smoothing
minutes: 30
level: beginner
goals: [Compute simple exponential smoothing by hand, Explain what alpha does, Show that the weights of old data decay exponentially, Fit alpha by minimising one-step errors, Know what SES cannot do]
prereqs: [s3-01-baselines]
tags: [ses, exponential-smoothing, ets]
skills: [from-scratch, baseline-first]
---

## Warm-up

```check
{"q": "The naive forecast uses only...", "type": "single",
 "options": ["The last value", "The average of all values", "The first value"],
 "answer": 0,
 "why": ["Correct: naive = the last observed value.", "That is the mean forecast.", "The first value is not used by naive."]}
```

```check
{"q": "The mean forecast gives every past value...", "type": "single",
 "options": ["The same weight", "A higher weight for recent values", "Zero weight"],
 "answer": 0,
 "why": ["Correct: every value counts the same in a plain average.", "Plain averages do not favour recent data. Exponential smoothing does.", "Every value counts in a mean."]}
```

## Why it matters

Naive uses only the last value. It reacts fast, but it copies the noise. The mean uses everything. It is calm, but it reacts very slowly when the [[level]] changes. Simple [[exponential smoothing]] (SES) sits **between** the two. It is a weighted average where **recent values count more**. It is simple, fast, and one of the strongest methods for series with no trend and no season. It is also the base of the whole [[ETS]] family.

## The update rule

SES keeps one number: the **level** l(t), our best estimate of the current "normal" value.

l(t) = α·y(t) + (1 − α)·l(t−1)

The forecast for every future step is the last level: ŷ(t+h) = l(t).

- y(t): the new observation.
- l(t−1): the old level.
- α (alpha): the **[[smoothing parameter]]**, between 0 and 1. It sets how fast the level reacts.

Same rule, written with the error e(t) = y(t) − l(t−1):

l(t) = l(t−1) + α·e(t)

The level moves a fraction α of the way toward the new value.

Numbers: α = 0.5 and data 10, 14, 12, 16. Start with l(1) = 10.
- y = 14: error = 14 − 10 = 4, l = 10 + 0.5·4 = 12.
- y = 12: error = 0, l = 12.
- y = 16: error = 4, l = 14.

The forecast for all future steps is 14.

```widget
{"name": "ses-alpha", "params": {"alpha": 0.3}}
```

```check
{"q": "α = 0.2, the old level is 50 and the new value is 60. What is the new level?", "type": "numeric",
 "answer": 52, "tol": 0.001,
 "why": "l = 50 + 0.2 * (60 - 50) = 52."}
```

## What alpha means

- **α close to 1**: the level follows the latest value. With α = 1 SES is the **naive** forecast.
- **α close to 0**: the level changes slowly. It is close to a long-run average.
- Small α suits noisy data with a stable level. Large α suits data where the level shifts.

Why "exponential"? If you open up the rule, the weight of the value k steps back is α·(1 − α)^k.

| Steps back k | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| weight, α = 0.3 | 0.300 | 0.210 | 0.147 | 0.103 | 0.072 |

The weights shrink by the same factor each step. That is an exponential decay. All weights together add up to 1 (there is also a small weight on the start level).

```chart
{"title": "Weights of past values for alpha = 0.3 and alpha = 0.7 (k = steps back)", "x": "k", "height": 200,
 "series": [
  {"name": "alpha 0.3", "kind": "bar", "x": [0,1,2,3,4,5,6,7], "y": [0.3, 0.21, 0.147, 0.103, 0.072, 0.050, 0.035, 0.025]},
  {"name": "alpha 0.7", "kind": "bar", "x": [0,1,2,3,4,5,6,7], "y": [0.7, 0.21, 0.063, 0.019, 0.006, 0.002, 0.0006, 0.0002]}
 ],
 "caption": "A large alpha puts almost all weight on the newest values. A small alpha remembers longer."}
```

```check
{"q": "With α = 0.5, what is the weight of the value 2 steps back?", "type": "numeric",
 "answer": 0.125, "tol": 0.0005,
 "why": "Weight = α(1 - α)^k = 0.5 * 0.5^2 = 0.125."}
```

## Choosing alpha and the start level

**Start level:** the usual choice is l(1) = y(1). Another choice is the mean of the first few values. With a long history, the choice matters little.

**Alpha:** pick the value that minimises the **sum of squared one-step errors** (SSE):

SSE(α) = Σ (y(t) − ŷ(t))², with ŷ(t) = l(t−1)

Do not use the test data. A simple method is a grid: try α = 0.05, 0.10, ..., 1.00 and keep the best. Libraries do the same with an optimiser.

If the best α is very close to 1, the series behaves like a [[random walk]]. If it is near 0, the series is close to noise around a fixed level.

```check
{"q": "You fit SES and the best alpha is 0.98. What does it tell you?", "type": "single",
 "options": ["The series behaves like a random walk: naive is almost as good", "The series has a strong season", "The model failed to converge"],
 "answer": 0,
 "why": ["Correct: alpha near 1 means the best forecast is nearly the last value.", "SES does not model a season. The alpha value does not show one.", "The result is a valid answer. Alpha can be near 1."]}
```

## Limits of SES

SES has **no trend** and **no season**. The forecast is a flat line. If the data goes up steadily, SES [[lag|lags]] behind and is always too low. The next lessons add a trend (Holt) and a season ([[Holt-Winters]]). Use SES for stable-level data, for example the demand of a product with no trend.

## Worked example

We write SES, grid-search alpha on the first part of a series, and forecast.

```python
import numpy as np

def ses_errors(y, alpha):
    # returns one-step errors e(t) = y(t) - l(t-1) for t = 2..n and the final level
    level = y[0]                     # start level = first value
    errors = []
    for value in y[1:]:
        e = value - level            # the forecast of this step is the old level
        errors.append(e)
        level = level + alpha * e    # update the level
    return np.array(errors), level

y = np.array([10, 14, 12, 16], dtype=float)
errors, level = ses_errors(y, 0.5)
print("errors:", errors, "final level:", level)

# Grid search on a noisy series whose level jumps from 50 to 60
rng = np.random.default_rng(1)
series = np.concatenate([np.full(30, 50.0), np.full(30, 60.0)]) + rng.normal(0, 2, 60)
grid = np.round(np.arange(0.05, 1.0001, 0.05), 2)
sse = [np.sum(ses_errors(series, a)[0] ** 2) for a in grid]
best = grid[int(np.argmin(sse))]
print("best alpha:", best, "SSE:", round(min(sse), 1))
print("forecast for next 3 steps:", np.round([ses_errors(series, best)[1]] * 3, 2))
# Output:
# errors: [4. 0. 4.] final level: 14.0
# best alpha: 0.55 SSE: 425.5
# forecast for next 3 steps: [59.09 59.09 59.09]
```

## Common mistakes

- Choosing alpha by looking at the test error.
- Expecting SES to follow a trend or a season. It gives a flat forecast.
- Starting the level at zero instead of the first value. The first forecasts will be far off.
- Mixing up alpha: a large alpha means fast reaction, not strong smoothing.
- Updating the level with the future value (using y(t) in the forecast of y(t)).

## Interview lens

**Typical question:** "What is exponential smoothing and what does alpha control?"

**Strong answer:** Simple exponential smoothing keeps a level that is a weighted average of past values, where the weights decay exponentially. The update is l(t) = α·y(t) + (1 − α)·l(t−1), and the forecast is flat at the last level. A large α reacts fast, with α = 1 giving the [[naive forecast]]. A small α gives a smooth level. I choose α by minimising the one-step squared error on the training data. SES does not handle trend or season, so I would use Holt or Holt-Winters for those.

**Red flags:** Saying "alpha is the amount of smoothing" the wrong way round. Believing SES can forecast a trend. Tuning alpha on the test set.

## Real world

- Exponential smoothing goes back to work by Robert Brown in the 1950s on inventory control, and to Charles Holt. The idea stayed popular because it is cheap to compute for thousands of products.
- Forecasting libraries such as statsmodels and statsforecast provide SES, often as the first method for items with a stable level.

## Key points

- SES: l(t) = α·y(t) + (1 − α)·l(t−1). The forecast is flat at the last level.
- α = 1 is naive. A small α is a slow average. Weights of old data decay by (1 − α) each step.
- Fit α by minimising the one-step squared error on training data only.
- SES has no trend and no season. Use Holt and Holt-Winters for those.
