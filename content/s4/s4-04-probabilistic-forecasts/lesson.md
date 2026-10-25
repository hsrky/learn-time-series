---
id: s4-04-probabilistic-forecasts
title: Quantiles, intervals and pinball loss
minutes: 30
level: intermediate
goals: [Read quantile forecasts and prediction intervals, Compute pinball loss and interval score, Check coverage and explain calibration versus sharpness]
prereqs: [s4-03-point-metrics]
tags: [uncertainty, quantile, pinball, coverage]
skills: [uncertainty, metrics, from-scratch]
---
## Warm-up
```check
{"q": "Which metric divides the total error by the total actual value?", "type": "single",
 "options": ["MAPE", "WAPE", "RMSE"],
 "answer": 1,
 "why": ["MAPE divides each error by its own actual and then averages.", "Correct: WAPE = sum of errors / sum of actuals.", "RMSE is in the units of the data and has no division by actuals."]}
```

```check
{"q": "Actual: 10, 20. Forecast: 14, 18. What is the MAE?", "type": "numeric",
 "answer": 3, "tol": 0.001,
 "why": "Errors are 4 and 2. The mean is 3."}
```

## Why it matters
A store manager asks: "How many loaves of bread will we sell tomorrow?" You say "100". The manager bakes 100. Sometimes the bread runs out. Sometimes it is wasted. A better answer is: "Probably 90 to 115. And we are 90% sure that it is below 120." Now the manager can decide how much risk to take. **A forecast without uncertainty is half a forecast.** This lesson shows how to state and score uncertainty.

## Quantiles
A [[quantile]] is a cut point in the distribution of possible outcomes. The `τ`-quantile is a value `q`. The actual falls below `q` with probability `τ`. (τ is read "tau". It is a number from 0 to 1.)

- The 0.5 quantile is the **median**: half of the outcomes are below it.
- The 0.9 quantile (P90): 90% of the outcomes are below it.
- The 0.1 quantile (P10): only 10% are below it.

Example: tomorrow's sales forecast is P10 = 85, P50 = 100, P90 = 118. Chance of selling less than 85 is 10%. Chance of selling more than 118 is 10%.

```check
{"q": "The P90 forecast is 118. What does that mean?", "type": "single",
 "options": ["Sales will be 118 in 90% of the days", "The model believes that sales are below 118 with 90% probability", "The error is 90%"],
 "answer": 1,
 "why": ["P90 is an upper cut point, not the most likely value.", "Correct: 90% of the probability is below 118.", "P90 says nothing about the error percentage."]}
```

## Pinball loss: how to score a quantile
How do you score a P90 forecast? The error of one point is not enough. Being too low is worse than being too high for P90, because P90 should be high. The [[pinball loss]] (also called quantile loss) handles this.

For one actual `y` and a quantile forecast `q` at level `τ`:

- If `y ≥ q` (forecast too low): loss = `τ × (y − q)`
- If `y < q` (forecast too high): loss = `(1 − τ) × (q − y)`

## Pinball loss: a worked case

Example, τ = 0.9, actual y = 100:

- q = 90 (too low by 10): loss = 0.9 × 10 = **9**
- q = 110 (too high by 10): loss = 0.1 × 10 = **1**

So a P90 forecast pays 9 times more for being low. To get a low loss on average, the model must put P90 high, where 90% of the outcomes are below. At τ = 0.5 the loss is half of the absolute error.

```widget
{"name": "quantile-loss", "params": {"tau": 0.9}}
```

```check
{"q": "τ = 0.1, actual y = 50, forecast q = 60. What is the pinball loss?", "type": "numeric",
 "answer": 9, "tol": 0.001,
 "why": "The forecast is too high (y < q). Loss = (1 − τ) × (q − y) = 0.9 × 10 = 9."}
```

## Prediction intervals, coverage, interval score
A [[prediction interval]] gives a lower and an upper value. An 80% interval is often `[P10, P90]`. We expect 80% of the actuals to fall inside.

The **[[coverage|empirical coverage]]** is the fraction of actuals that really fall inside. Good intervals have coverage close to the nominal level. Coverage 60% for an 80% interval means the model is **overconfident**.

## Sharpness and the interval score

Coverage alone is not enough. An interval from minus infinity to plus infinity has 100% coverage and no use. So we also want **sharp** (narrow) intervals. The **[[interval score]]** (Winkler score) combines both. For an interval `[l, u]`, level `1 − α`, and actual `y`:

The score is `(u − l)`. Add `(2/α)·(l − y)` if `y < l`. Add `(2/α)·(y − u)` if `y > u`.

- `(u − l)` is the width. Narrow is good.
- The penalty applies only when `y` is outside. It is larger for small `α` (high confidence).

Example, 80% interval (α = 0.2, 2/α = 10): `[90, 110]`, actual 120. Width 20, miss 10, penalty 10 × 10 = 100. Score = **120**. If the actual were 100, the score would be 20. Lower is better.

```check
{"q": "80% interval [90, 110]. Actual = 85. What is the interval score?", "type": "numeric",
 "answer": 70, "tol": 0.001,
 "why": "Width = 20. The actual is below the lower bound by 5. Penalty = (2/0.2) × 5 = 50. Score = 20 + 50 = 70."}
```

## Calibration, sharpness and CRPS
- [[calibration|Calibration]]: the stated probabilities match reality (80% intervals contain 80% of the actuals).
- **[[sharpness|Sharpness]]**: the intervals are narrow.

Aim: be calibrated first, then as sharp as possible.

The **[[crps|CRPS]]** (continuous ranked probability score) scores a whole forecast distribution with one number. It is a generalization of MAE: if the forecast is a single value, CRPS equals the absolute error. Idea: CRPS is the pinball loss averaged over **all** quantile levels (times 2). In practice, people average pinball loss over a grid, for example 0.1, 0.2, ..., 0.9. Many benchmarks report a scaled version, sometimes called weighted quantile loss (wQL).

```chart
{"title": "A calibrated and an overconfident 80% interval", "x": "day", "height": 240,
 "series": [
   {"name": "actual", "gen": [["const", {"value": 100}], ["noise", {"sd": 10}]], "n": 40, "seed": 8},
   {"name": "calibrated P90", "gen": [["const", {"value": 112.8}]], "n": 40, "dash": true},
   {"name": "calibrated P10", "gen": [["const", {"value": 87.2}]], "n": 40, "dash": true},
   {"name": "overconfident P90", "gen": [["const", {"value": 106.4}]], "n": 40},
   {"name": "overconfident P10", "gen": [["const", {"value": 93.6}]], "n": 40}
 ],
 "caption": "The narrow band misses many actuals. It looks sharp but it is not calibrated."}
```

```check
{"q": "A model gives 90% intervals. In a backtest, 70% of the actuals are inside. What do you conclude?", "type": "single",
 "options": ["The model is well calibrated", "The intervals are too narrow (overconfident)", "The intervals are too wide"],
 "answer": 1,
 "why": ["Good calibration would give about 90%.", "Correct: too few actuals fall inside, so the intervals should be wider.", "Too wide intervals would cover more than 90%."]}
```

## Worked example
We have 200 actual days from a normal distribution with mean 100 and sd 10. Model A knows the truth (sd = 10). Model B thinks sd = 5 (overconfident). Both give P10, P50, P90.

```python
import numpy as np

rng = np.random.default_rng(4)
y = 100 + 10 * rng.standard_normal(200)       # actual values
z90 = 1.2816                                   # z-score of the 90% quantile

def quantiles(sd):
    return {0.1: np.full(200, 100 - z90 * sd),
            0.5: np.full(200, 100.0),
            0.9: np.full(200, 100 + z90 * sd)}

def pinball(y, q, tau):
    d = y - q
    return np.mean(np.where(d >= 0, tau * d, (tau - 1) * d))

def interval_score(y, lo, hi, alpha):
    width = hi - lo
    below = (2 / alpha) * np.maximum(lo - y, 0)
    above = (2 / alpha) * np.maximum(y - hi, 0)
    return np.mean(width + below + above)

for name, sd in [("A calibrated", 10), ("B overconfident", 5)]:
    q = quantiles(sd)
    cov = np.mean((y >= q[0.1]) & (y <= q[0.9]))
    print(name,
          "| coverage:", round(cov, 3),
          "| pinball P90:", round(pinball(y, q[0.9], 0.9), 3),
          "| interval score:", round(interval_score(y, q[0.1], q[0.9], 0.2), 2))
# Output:
# A calibrated | coverage: 0.805 | pinball P90: 1.708 | interval score: 35.3
# B overconfident | coverage: 0.46 | pinball P90: 2.295 | interval score: 44.51
```

Model A has coverage close to 80% and the better (lower) scores. Model B is sharper but covers much less, and both scores are worse.

## Common mistakes
- Judging intervals by width only. Always check coverage.
- Checking coverage on training data. Use a backtest or a test period.
- Training a quantile model for P90 and then reporting its MAE.
- Mixing "90% interval" with "P90". A 90% interval is usually `[P5, P95]`.
- Letting quantiles cross (P90 below P50). Sort them or use a method that prevents it.
- Ignoring the horizon: uncertainty grows with the horizon, so coverage must be checked per step.

## Interview lens
**Typical question:** "How would you evaluate a probabilistic forecast?"

**Strong answer:** I look at two things: calibration and sharpness. For calibration I compute the empirical coverage of each interval on a backtest and compare it with the nominal level. For overall quality I use the pinball loss for each quantile. I average it over a grid of quantile levels, which approximates CRPS. For intervals I also use the interval score, which adds a penalty for misses to the width. I compare with a simple baseline, such as seasonal naive with intervals from past residuals. And I check coverage by horizon step.

**Red flags:**
- Only reporting MAE for a quantile model.
- Claiming "95% interval" with no coverage check.
- Not knowing what pinball loss penalizes.
- Confusing P90 with a 90% interval.

## Real world
- Amazon's DeepAR (a published paper) outputs a full forecast distribution and is evaluated with quantile losses.
- The M5 competition had an "Uncertainty" track: teams submitted nine quantiles and were scored with a weighted scaled pinball loss.
- Retailers use a high quantile (for example P90) for items where running out is more costly than waste. This is the idea of the [[newsvendor problem]].

## Key points
- A quantile forecast says: the actual is below this value with probability τ.
- Pinball loss weights under- and over-forecasts by τ and 1 − τ. It is the right score for a quantile.
- A prediction interval is judged by coverage (close to nominal) and width (narrow).
- Interval score = width + penalty for misses. Lower is better.
- CRPS is the pinball loss averaged over all quantile levels; it generalizes MAE.
