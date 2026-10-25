---
id: s3-04-holt-winters-ets
title: Holt-Winters and the ETS family
minutes: 35
level: intermediate
goals: [Add a seasonal part to exponential smoothing, Choose additive or multiplicative seasonality, Read the ETS naming (Error, Trend, Season), Match classic methods to ETS names, Implement Holt-Winters in numpy]
prereqs: [s3-03-holt-trend-damped]
tags: [holt-winters, ets, seasonality]
skills: [from-scratch, baseline-first]
---

## Warm-up

```check
{"q": "Holt's method with level 80 and trend 2 gives what forecast for h = 5?", "type": "numeric",
 "answer": 90, "tol": 0.001,
 "why": "80 + 5 * 2 = 90."}
```

```check
{"q": "What does a damped trend do?", "type": "single",
 "options": ["The trend fades each step, so the forecast flattens", "The level is ignored", "The season is removed"],
 "answer": 0,
 "why": ["Correct: the trend is multiplied by phi (below 1) at each step.", "The level stays in the model.", "A damped trend is not about the season."]}
```

## Why it matters

Daily sales have a weekly pattern. Electricity use has a daily pattern. [[Holt's method]] cannot see a repeating pattern. **[[Holt-Winters]]** (Winters, 1960) adds a third state: the **season**. It is a classic that is still fast and strong. It is also the base of the **[[ETS]]** framework used by many forecasting tools. Interviewers ask when to use additive and when to use [[multiplicative season|multiplicative seasonality]].

## Holt-Winters: three states

The method keeps a [[level]], a trend and a set of seasonal values. There is one seasonal value for each position in the season. That makes m values: m = 7 for a weekly pattern in daily data.

Additive version:

- Forecast: ŷ(t+h) = l(t) + h·b(t) + s(t+h−m)
- Level: l(t) = α·(y(t) − s(t−m)) + (1 − α)·(l(t−1) + b(t−1))
- Trend: b(t) = β·(l(t) − l(t−1)) + (1 − β)·b(t−1)
- Season: s(t) = γ·(y(t) − l(t−1) − b(t−1)) + (1 − γ)·s(t−m)

Symbols:

- γ (gamma): speed of the seasonal update, between 0 and 1.
- s(t−m): the seasonal value from one full season ago.
- (y(t) − s(t−m)): the value with the season removed ("seasonally adjusted").

Idea in words: remove the old season from the new value to update the level. Then compare the value with what the level and trend expected, and use the gap to update the season.

Numbers: the new value is 130, the old seasonal value is +20, so the adjusted value is 110. If the level plus trend was 100, the season gap is 130 − 100 = 30. With γ = 0.2 the new season is 0.2·30 + 0.8·20 = 22.

```widget
{"name": "holt-winters", "params": {"alpha": 0.3, "beta": 0.1, "gamma": 0.2}}
```

```check
{"q": "γ = 0.5, old seasonal value s(t-m) = 10, and the gap y(t) - l(t-1) - b(t-1) = 18. What is the new seasonal value?", "type": "numeric",
 "answer": 14, "tol": 0.001,
 "why": "0.5 * 18 + 0.5 * 10 = 14."}
```

## Additive or multiplicative?

- **[[Additive season]]:** the seasonal swing has a constant size. "Sundays are 20 units higher." Use it when the swings look the same size at all levels.
- **Multiplicative season:** the swing is proportional to the level. "Sundays are 25% higher." Use it when the swings grow with the series.

The multiplicative version divides and multiplies instead of subtracting and adding. The forecast is ŷ(t+h) = (l(t) + h·b(t))·s(t+h−m). The level update uses y(t)/s(t−m).

Quick test: plot the series. If the seasonal peaks get taller as the level rises, use multiplicative (or take the log first and use additive).

```chart
{"title": "Additive season (constant swing) and multiplicative season (swing grows)", "x": "month", "height": 240,
 "series": [
  {"name": "additive", "y": [20.0, 23.0, 25.3, 26.5, 26.3, 25.0, 23.0, 21.0, 19.7, 19.5, 20.7, 23.0, 26.0, 29.0, 31.3, 32.5, 32.3, 31.0, 29.0, 27.0, 25.7, 25.5, 26.7, 29.0, 32.0, 35.0, 37.3, 38.5, 38.3, 37.0, 35.0, 33.0, 31.7, 31.5, 32.7, 35.0, 38.0, 41.0, 43.3, 44.5, 44.3, 43.0, 41.0, 39.0, 37.7, 37.5, 38.7, 41.0]},
  {"name": "multiplicative", "y": [20.0, 23.1, 25.5, 26.9, 26.8, 25.3, 23.0, 20.6, 18.8, 18.4, 19.6, 22.3, 26.0, 29.8, 32.8, 34.4, 34.1, 32.1, 29.0, 25.8, 23.5, 22.9, 24.3, 27.6, 32.0, 36.6, 40.1, 41.9, 41.4, 38.8, 35.0, 31.1, 28.2, 27.4, 29.0, 32.8, 38.0, 43.3, 47.4, 49.4, 48.7, 45.6, 41.0, 36.3, 32.9, 31.9, 33.7, 38.1]}
 ],
 "caption": "Both series have the same trend. The swing of the additive one stays the same. The swing of the multiplicative one grows."}
```

```check
{"q": "Weekly retail sales: a Saturday is always about 30% higher than a Tuesday, at any level of sales. Which season type?", "type": "single",
 "options": ["Multiplicative", "Additive", "No season"],
 "answer": 0,
 "why": ["Correct: a fixed percentage means the swing is proportional to the level.", "Additive means a fixed number of units, such as +50 at any level.", "There is a clear weekly pattern."]}
```

## The ETS family: a naming system

**ETS** stands for **E**rror, **T**rend, **S**eason. Each part has a type. The model is written ETS(Error, Trend, Season).

| Part | Choices |
|---|---|
| Error | A (additive), M (multiplicative) |
| Trend | N (none), A (additive), Ad (additive damped) |
| Season | N (none), A (additive), M (multiplicative) |

Familiar methods are special cases:

| Method | ETS name |
|---|---|
| Simple exponential smoothing | ETS(A,N,N) |
| Holt linear trend | ETS(A,A,N) |
| Damped trend | ETS(A,Ad,N) |
| Additive Holt-Winters | ETS(A,A,A) |
| Multiplicative Holt-Winters | ETS(A,A,M) or ETS(M,A,M) |

The **error type** matters for the [[prediction interval]]s and the likelihood. ETS is a full statistical model (a state-space model), so it gives intervals and an [[AIC]]. Tools such as the R `forecast` package and `statsmodels.tsa.exponential_smoothing.ets.ETSModel` can fit many ETS models and choose the best by AIC (corrected: AICc).

```check
{"q": "Which ETS name is simple exponential smoothing with additive errors?", "type": "single",
 "options": ["ETS(A,N,N)", "ETS(A,A,N)", "ETS(A,A,A)"],
 "answer": 0,
 "why": ["Correct: no trend (N) and no season (N).", "This has an additive trend. It is Holt's method.", "This has trend and season. It is additive Holt-Winters."]}
```

## Start values and limits

- You need at least **two full seasons** of data. The start values come from the first season(s).
- The method has **three** [[smoothing parameter]]s (α, β, γ) plus start values. Fit them by minimising the one-step squared error on training data.
- Only **one** [[season length]]. For data with two seasons (daily and weekly in hourly data), use other models.
- Holt-Winters is robust and fast. For thousands of series it is a strong default.

## Worked example

We code additive Holt-Winters in a compact form. We apply it to a weekly series. Then we compare it with the [[seasonal naive]] [[baseline]] on 28 held-out days.

```python
import numpy as np

def holt_winters_add(y, m, alpha, beta, gamma, h):
    n = len(y)
    centre = y[:m].mean()
    trend = (y[m:2 * m].mean() - centre) / m
    line = centre + trend * (np.arange(m) - (m - 1) / 2)
    season = y[:m] - line
    level = line[-1]
    for t in range(m, n):
        i = t % m
        expected = level + trend
        new_level = alpha * (y[t] - season[i]) + (1 - alpha) * expected
        season[i] = gamma * (y[t] - expected) + (1 - gamma) * season[i]
        trend = beta * (new_level - level) + (1 - beta) * trend
        level = new_level
    return np.array([level + j * trend + season[(n - 1 + j) % m] for j in range(1, h + 1)])

rng = np.random.default_rng(7)
t = np.arange(140)
y = 100 + 0.2 * t + 15 * np.sin(2 * np.pi * t / 7) + rng.normal(0, 3, 140)
train, test = y[:112], y[112:]           # 16 weeks to fit, 4 weeks to test

hw = holt_winters_add(train, 7, 0.2, 0.02, 0.1, 28)
snaive = np.tile(train[-7:], 4)          # repeat the last week 4 times

mae = lambda f: np.mean(np.abs(test - f))
print("Holt-Winters MAE:  ", round(mae(hw), 2))
print("Seasonal naive MAE:", round(mae(snaive), 2))
print("skill:", round(1 - mae(hw) / mae(snaive), 2))
# Output:
# Holt-Winters MAE:   2.84
# Seasonal naive MAE: 3.24
# skill: 0.12
```

## Common mistakes

- Using additive seasonality when the swings clearly grow with the level (and the reverse).
- Fitting with fewer than two full seasons.
- Setting the season length wrongly, for example 12 for weekly data.
- Letting γ (or β) be large on noisy data. The season (or the trend) then chases noise.
- Comparing with the naive baseline only. For seasonal data the right baseline is seasonal naive.

## Interview lens

**Typical question:** "Explain Holt-Winters. When would you pick multiplicative seasonality?"

**Strong answer:** Holt-Winters has three states: level, trend, and a set of seasonal values, with smoothing parameters α, β and γ. Each step it removes the old seasonal value to update the level. Then it updates the seasonal value from the gap between the data and the expectation. I pick additive seasonality when the seasonal swing has the same size at all levels. I pick multiplicative when the swing grows with the level, or I take the log and use additive. In ETS notation these are ETS(A,A,A) and ETS(M,A,M). I compare the result with a seasonal naive baseline.

**Red flags:** Not knowing what the three parameters do. Saying Holt-Winters handles several seasons. Skipping the seasonal naive comparison.

## Real world

- Peter Winters published the seasonal extension of Holt's method in 1960. It is one of the oldest forecasting methods still in daily use.
- Rob Hyndman and colleagues created the ETS state-space framework (2002). It underlies the `ets` function in the R forecast package, and similar models exist in statsmodels and statsforecast.

## Key points

- Holt-Winters = level + trend + season, with parameters α, β, γ. Needs at least two full seasons.
- Additive season: constant swing. Multiplicative season: swing proportional to the level.
- ETS(Error, Trend, Season) names the family: SES = ETS(A,N,N), Holt = ETS(A,A,N), additive HW = ETS(A,A,A).
- Fit parameters on training data and always compare with seasonal naive.
