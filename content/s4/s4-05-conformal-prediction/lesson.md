---
id: s4-05-conformal-prediction
title: Conformal prediction for time series
minutes: 30
level: advanced
goals: [Build split conformal intervals from calibration residuals, Explain why time series break the basic guarantee, Use rolling and adaptive conformal ideas to stay calibrated]
prereqs: [s4-04-probabilistic-forecasts]
tags: [uncertainty, conformal, intervals, trend]
skills: [uncertainty, from-scratch, backtest]
---
## Warm-up
```check
{"q": "An 80% interval has an empirical coverage of 55% in a backtest. What is the problem?", "type": "single",
 "options": ["The intervals are too wide", "The intervals are too narrow", "The model has high bias"],
 "answer": 1,
 "why": ["Wide intervals would cover more than 80%.", "Correct: too few actuals fall inside, so the intervals must be wider.", "Bias is a different question. Coverage only counts how often actuals are inside."]}
```

```check
{"q": "Which score adds a penalty when the actual is outside the interval?", "type": "single",
 "options": ["Pinball loss at τ = 0.5", "Interval (Winkler) score", "MAPE"],
 "answer": 1,
 "why": ["Pinball loss scores a single quantile, not an interval with two ends.", "Correct: width plus a penalty for each miss.", "MAPE is a point metric."]}
```

## Why it matters
Most intervals come from a formula that assumes the errors are normal (a bell shape). If the assumption is wrong, the interval is wrong. **[[conformal prediction|Conformal prediction]]** is a simple method that makes almost no assumptions. You take your own past errors and use them to set the interval width. If the errors are exchangeable (the order does not matter), the interval has a coverage guarantee. It works with any model, even a black box. Since 2023 it appears in many forecasting interviews and libraries.

## Split conformal: the recipe
Use three parts of the data.

1. **Train** part: fit any model.
2. **[[calibration set|Calibration]]** part: predict it and compute the **absolute [[residual|residuals]]** `r = |y − ŷ|`.
3. **Test**: new points. The interval is `ŷ ± q`.

How to choose `q`? With `n` calibration residuals and miss rate `α` (0.2 for an 80% interval), take the `k`-th smallest residual, where

`k = ceil((n + 1) × (1 − α))`

- `n` is the number of calibration residuals.
- `(n + 1)` is a small correction. It makes the guarantee exact for finite `n`.
- If `k > n`, there are too few residuals. Use an infinite interval.

Example: `n = 9`, α = 0.2. Then `k = ceil(10 × 0.8) = 8`. Residuals: 1, 2, 2, 3, 3, 4, 5, 6, 9. The 8th smallest is **6**. So the interval is `ŷ ± 6`.

```widget
{"name": "conformal", "params": {}}
```

```check
{"q": "n = 19 calibration residuals, α = 0.1. Which rank k do you use?", "type": "numeric",
 "answer": 18, "tol": 0.001,
 "why": "k = ceil((19 + 1) × 0.9) = ceil(18) = 18. Take the 18th smallest residual."}
```

## What the guarantee says
Suppose calibration points and the new point are **[[exchangeable]]**. This means they come from the same process, and their order does not matter. Then the chance that the new actual lies in the interval is **at least** `1 − α`. This holds for any model and any error shape.

Two notes:
- The guarantee is **marginal**: it is true on average over all points. It is not true for every single situation. Maybe the interval is too narrow on holidays and too wide on quiet days.
- To let the width change with the situation, divide residuals by a local scale estimate. This is called normalized conformal. We do not cover it here.

```check
{"q": "The conformal guarantee needs which main assumption?", "type": "single",
 "options": ["The errors are normal", "Calibration and test points are exchangeable", "The model is linear"],
 "answer": 1,
 "why": ["Conformal methods do not need normal errors. That is their main benefit.", "Correct: the order must not matter, roughly the same process for all points.", "Any model can be used."]}
```

## Why time series break it
Time series are **not** exchangeable.

- Neighbouring errors are correlated ([[autocorrelation]]).
- The world changes: trend, new volatility, a promotion, a new season.

If the noise grows after the calibration period, the old residuals are too small. The intervals under-cover. Look at the chart: the noise grows at day 250.

```chart
{"title": "Noise grows after day 60: a fixed band stops covering", "x": "day", "height": 230, "series": [{"name": "series", "y": [50.2, 49.5, 49.6, 47.6, 51.8, 51.1, 49.7, 50.8, 50.3, 49.4, 51.0, 49.7, 49.7, 49.2, 50.5, 49.9, 50.5, 49.4, 50.1, 49.1, 50.8, 50.2, 50.3, 50.4, 49.0, 50.8, 52.1, 48.4, 48.3, 48.5, 50.8, 50.1, 51.1, 50.7, 50.2, 50.3, 49.8, 50.9, 48.9, 49.6, 50.2, 51.8, 49.2, 48.9, 49.4, 51.0, 49.8, 51.3, 48.1, 51.1, 51.0, 48.6, 50.2, 51.2, 50.1, 51.0, 52.4, 50.3, 49.7, 49.2, 51.9, 49.4, 49.5, 49.7, 51.9, 46.8, 45.4, 42.7, 53.6, 50.2, 54.5, 50.0, 47.8, 51.4, 49.8, 46.2, 47.3, 55.3, 51.1, 51.2, 49.2, 47.9, 52.7, 49.7, 47.7, 49.6, 47.3, 50.6, 53.4, 47.5, 54.3, 48.0, 50.5, 47.5, 49.3, 50.1, 48.7, 47.9, 48.0, 47.5, 45.3, 49.2, 51.2, 52.7, 51.9, 57.4, 51.0, 48.6, 55.6, 46.9, 52.9, 47.1, 51.1, 44.1, 52.7, 49.5, 47.1, 55.0, 52.3, 50.1]}, {"name": "upper band (calm period)", "y": [51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6, 51.6], "dash": true}, {"name": "lower band (calm period)", "y": [48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4, 48.4], "dash": true}], "marks": [{"x": 60, "label": "volatility rises"}], "caption": "The dashed band was fitted in the calm period. After day 60 many points are outside. Rolling conformal updates the band."}
```

## Fixes: rolling and adaptive conformal
- **[[rolling-window conformal|Rolling-window conformal]].** For each new point, use only the last `W` residuals (for example 60). Old errors are forgotten. After a change in volatility, the band adapts in about `W` steps. A residual is known only after its actual arrives. To forecast day `t` one step ahead, use residuals of days up to `t − 1`. For an `h`-step forecast of day `t`, use `h`-step residuals of days up to `t − h`.
## Fixes: adaptive conformal and EnbPI

- **[[adaptive conformal inference|Adaptive conformal inference (ACI)]].** Keep a working miss rate `α_t`. After each step, update:
   `α_{t+1} = α_t + γ · (α − err_t)`
   - `err_t` is 1 if the actual missed the interval, otherwise 0.
   - `γ` (gamma) is a small step size, for example 0.01.
   - If you miss too often, `α_t` falls, so the intervals become wider.
- **[[enbpi|EnbPI]]** (ensemble batch prediction intervals): train an ensemble on bootstrap samples of the series. Collect out-of-sample residuals from the ensemble. Update the residual set as new data arrives. It targets time series without needing a separate calibration set.

```check
{"q": "In ACI, the interval missed the actual (err = 1). What happens to α_t?", "type": "single",
 "options": ["It increases, so the interval gets narrower", "It decreases, so the interval gets wider", "It stays the same"],
 "answer": 1,
 "why": ["That would make more misses.", "Correct: α_{t+1} = α_t + γ(α − 1) is smaller, so the target coverage is higher and the interval is wider.", "ACI changes α_t after every step."]}
```

## Worked example
The noise has sd 1 until day 250, then sd 3. Our forecaster is seasonal naive with period 7. We compare a static split conformal (calibrated once on days 7–199) with a rolling one (last 60 residuals).

```python
import numpy as np

rng = np.random.default_rng(0)
n, m, alpha = 400, 7, 0.2
t = np.arange(n)
sd = np.where(t < 250, 1.0, 3.0)
y = 50 + 5 * np.sin(2 * np.pi * t / m) + rng.normal(0, 1, n) * sd

yhat = np.full(n, np.nan)
yhat[m:] = y[:-m]                               # seasonal naive forecast
res = np.abs(y - yhat)                          # absolute residuals

def conformal_q(r, alpha):
    r = np.sort(r)
    k = int(np.ceil((len(r) + 1) * (1 - alpha)))
    return r[k - 1] if k <= len(r) else np.inf

# Static: one q from calibration days 7..199
q_static = conformal_q(res[m:200], alpha)

# Rolling: q from the last 60 residuals known at time t (days t-60 .. t-1)
W = 60
test = np.arange(250, n)
q_roll = np.array([conformal_q(res[tt - W:tt], alpha) for tt in test])

cov_static = np.mean(res[test] <= q_static)
cov_roll = np.mean(res[test] <= q_roll)
print("static q:", round(q_static, 2))
print("static coverage:", round(cov_static, 3))
print("rolling coverage:", round(cov_roll, 3))
print("mean rolling q:", round(q_roll.mean(), 2))
# Output:
# static q: 1.79
# static coverage: 0.313
# rolling coverage: 0.713
# mean rolling q: 4.47
```

The static band was calibrated in the calm period. After the volatility rises, it covers only a part of the actuals. The rolling band learns the new level of errors. Its coverage (0.71) is much closer to the 80% target, but it is still lower. The band needs about one window to catch up, and the first test days after the change are under-covered. Here the residual `|y − ŷ|` contains noise from both days, so it is larger than the noise itself.

## Common mistakes
- Calibrating on the training residuals of a model. They are too small. Use data the model did not see.
- Forgetting the `(n + 1)` correction. With a small `n` the coverage is then too low.
- Using future residuals in the rolling window. For horizon `h`, only residuals that are already known can be used.
- Trusting the guarantee after a regime change without monitoring coverage.
- Reporting only average coverage. Check coverage per horizon step and per period.

## Interview lens
**Typical question:** "How would you add prediction intervals to a black-box forecasting model?"

**Strong answer:** I would use conformal prediction. I keep a calibration window of recent backtest residuals that the model did not train on. I take the `⌈(n+1)(1−α)⌉`-th smallest absolute residual as the interval half-width, which needs no normal assumption. Time series are not exchangeable. So I use a rolling window of residuals, or adaptive conformal, which updates α online when coverage drifts. I compute residuals per horizon step. Then I check coverage in a backtest and monitor it in production.

**Red flags:**
- "Just use ±1.96 sd of the training residuals."
- Using in-sample residuals.
- Claiming the guarantee holds under any drift.
- Not knowing what exchangeable means.

## Real world
- The method was developed by Vladimir Vovk and colleagues. Angelopoulos and Bates wrote a widely read introduction (2021) with a gentle tutorial.
- Gibbs and Candès (2021) published adaptive conformal inference for data with distribution shift. Xu and Xie (2021) published EnbPI for time series.
- Libraries such as MAPIE and Darts offer conformal intervals for forecasts, and Nixtla's forecasting libraries also support conformal prediction intervals.

## Key points
- Split conformal: fit on train, take absolute residuals on calibration data, use the `⌈(n+1)(1−α)⌉`-th smallest as half-width.
- It works with any model and does not assume normal errors.
- The guarantee needs exchangeability. Time series break it with trend, drift and volatility changes.
- Use rolling-window residuals, ACI or EnbPI to stay calibrated, and always check coverage in a backtest.
