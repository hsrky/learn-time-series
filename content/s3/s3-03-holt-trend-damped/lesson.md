---
id: s3-03-holt-trend-damped
title: Holt linear trend and damped trend
minutes: 30
level: beginner
goals: [Add a trend to exponential smoothing, Compute the Holt update equations by hand, Explain what beta and phi control, Choose between linear and damped trend, Implement Holt in numpy]
prereqs: [s3-02-simple-exponential-smoothing]
tags: [holt, trend, damped, ets]
skills: [from-scratch]
---

## Warm-up

```check
{"q": "SES has alpha = 0.3, old level 40, new value 50. What is the new level?", "type": "numeric",
 "answer": 43, "tol": 0.001,
 "why": "40 + 0.3 * (50 - 40) = 43."}
```

```check
{"q": "Why does SES fail on a series that rises every week?", "type": "single",
 "options": ["Its forecast is a flat line, so it stays below the rising data", "Alpha must be zero", "SES needs a season"],
 "answer": 0,
 "why": ["Correct: SES has a level but no slope.", "Alpha can take any value between 0 and 1.", "SES has no season. A trend needs a slope term."]}
```

## Why it matters

Many business series have a trend: users, revenue, energy use. SES forecasts a flat line, so it is always late. **Holt's method** (1957) fixes this. It tracks two numbers: the **level** (where we are) and the **trend** (how fast we move). The forecast is a line. A small change, the **damped trend**, makes that line flatten over time. It is a common winner in forecasting benchmarks.

## Holt's linear trend

Two states: level l(t) and trend b(t) (the change per step).

- Forecast: ŷ(t+h) = l(t) + h·b(t)
- Level: l(t) = α·y(t) + (1 − α)·(l(t−1) + b(t−1))
- Trend: b(t) = β·(l(t) − l(t−1)) + (1 − β)·b(t−1)

Symbols:

- α (alpha): speed of the level update, between 0 and 1.
- β (beta): speed of the trend update, between 0 and 1.
- l(t−1) + b(t−1): what we expected the level to be now.

The level is a mix of the new value and the expected value. The trend is a mix of the latest observed change and the old trend.

Numbers: data 10, 12, 15 with α = β = 0.5. Start l = 10, b = 12 − 10 = 2.
- y = 12: l = 0.5·12 + 0.5·(10 + 2) = 12. b = 0.5·(12 − 10) + 0.5·2 = 2.
- y = 15: l = 0.5·15 + 0.5·(12 + 2) = 14.5. b = 0.5·(14.5 − 12) + 0.5·2 = 2.25.
- Forecast for h = 2: 14.5 + 2·2.25 = 19.

```widget
{"name": "holt-winters", "params": {"alpha": 0.5, "beta": 0.2}}
```

```check
{"q": "After an update the level is 100 and the trend is 3. What is Holt's forecast for h = 4?", "type": "numeric",
 "answer": 112, "tol": 0.001,
 "why": "100 + 4 * 3 = 112."}
```

## What beta does

- **β small** (0.05): the trend changes slowly. Good when the slope is stable. It is robust to noise.
- **β large** (0.5): the trend reacts to every change. The forecast can swing. Good when the slope changes often.

In practice the best β is often small. Noise in the last change would otherwise ruin the slope. Choose α and β together by minimising the sum of squared one-step errors on training data.

The forecast is a **straight line**. For a long horizon this line may go far above or below reality. A trend does not last forever. This is why we have the damped version.

## Damped trend

Add a number φ (phi) between 0 and 1 (often 0.8 to 0.98). Each step the trend is multiplied by φ, so it fades.

- Forecast: ŷ(t+h) = l(t) + (φ + φ² + ... + φ^h)·b(t)
- Level: l(t) = α·y(t) + (1 − α)·(l(t−1) + φ·b(t−1))
- Trend: b(t) = β·(l(t) − l(t−1)) + (1 − β)·φ·b(t−1)

Numbers: φ = 0.8, b = 2. The added trend part is 0.8·2 = 1.6 for h = 1. For h = 2: (0.8 + 0.64)·2 = 2.88. As h grows, the sum goes to φ/(1 − φ) = 4. So the forecast stops at l + 4·2 = l + 8. If φ = 1 you get Holt's linear method.

```chart
{"title": "Linear trend keeps rising. Damped trend flattens out.", "x": "time", "height": 230,
 "series": [
  {"name": "data", "y": [19.2, 19.7, 21.8, 23.4, 25.1, 25.1, 25.4, 26.2, 28.7, 30.6, 30.3, 29.8, 31.0, 34.6, 34.2, 33.3, 35.9, 35.8, 37.4, 38.5, 39.3, 41.6, 41.9, 42.4, 44.4, 45.8, 44.4, 46.7, 47.0, 48.8]},
  {"name": "Holt linear forecast", "dash": true, "x": [30,31,32,33,34,35,36,37,38,39,40,41], "y": [49.4, 50.4, 51.4, 52.3, 53.3, 54.3, 55.2, 56.2, 57.2, 58.1, 59.1, 60.0]},
  {"name": "damped trend forecast (phi 0.85)", "dash": true, "x": [30,31,32,33,34,35,36,37,38,39,40,41], "y": [48.5, 49.0, 49.3, 49.6, 49.9, 50.1, 50.3, 50.5, 50.6, 50.8, 50.9, 50.9]}
 ],
 "marks": [{"x": 30, "label": "forecast starts"}],
 "caption": "Both start from the same data. The damped forecast levels off, which is safer for a long horizon."}
```

```check
{"q": "With phi = 0.5 and trend b = 4, what is the total trend added to the level as h goes to infinity?", "type": "numeric",
 "answer": 4, "tol": 0.001,
 "why": "The sum phi + phi^2 + ... = phi / (1 - phi) = 0.5 / 0.5 = 1. Multiply by b: 1 * 4 = 4."}
```

## Which one to use

| Situation | Choice |
|---|---|
| Stable, strong, long-lasting trend and a short horizon | Holt linear |
| Long horizon, or you doubt the trend will continue | Damped trend |
| No clear trend | SES |

Rule of thumb: when unsure, try damped. It is a very strong benchmark in many comparisons, including the M-competitions on yearly and monthly data.

## Worked example

We implement Holt with an optional φ and compare the 10-step forecasts.

```python
import numpy as np

def holt(y, alpha, beta, h, phi=1.0):
    level, trend = y[0], y[1] - y[0]                 # start values from the first two points
    for value in y[1:]:
        new_level = alpha * value + (1 - alpha) * (level + phi * trend)
        trend = beta * (new_level - level) + (1 - beta) * phi * trend
        level = new_level
    steps = np.arange(1, h + 1)
    damp = np.cumsum(phi ** steps)                   # phi + phi^2 + ... + phi^h
    return level + damp * trend

y = np.array([10.0, 12.0, 15.0])
print("lesson example h=2:", holt(y, 0.5, 0.5, 2)[-1])

rng = np.random.default_rng(5)
t = np.arange(30)
series = 20 + 1.0 * t + rng.normal(0, 1, 30)         # steady slope of 1 per step
linear = holt(series, 0.5, 0.2, 10)
damped = holt(series, 0.5, 0.2, 10, phi=0.85)
print("last value:", round(series[-1], 1))
print("linear h=1, h=10:", round(linear[0], 1), round(linear[9], 1))
print("damped h=1, h=10:", round(damped[0], 1), round(damped[9], 1))
# Output:
# lesson example h=2: 19.0
# last value: 48.8
# linear h=1, h=10: 49.5 58.2
# damped h=1, h=10: 48.6 50.8
```

## Common mistakes

- Using Holt for a long horizon on a trend that will not continue. The forecast explodes.
- Setting β too large on noisy data. The slope swings and the forecast is unstable.
- Forgetting that damped trend needs φ below 1. With φ = 1 it is the linear version.
- Using Holt on seasonal data. It cannot model a season. Use Holt-Winters.
- Starting the trend at zero when the data clearly rises. The first forecasts are poor.

## Interview lens

**Typical question:** "How does Holt's method extend simple exponential smoothing, and when would you use a damped trend?"

**Strong answer:** Holt adds a second state, the trend, next to the level. The level update mixes the new value with the expected level (previous level plus trend). The trend update mixes the latest level change with the old trend. The forecast is a straight line from the last level. A damped trend multiplies the trend by φ below 1 each step, so the forecast flattens. I use damped for long horizons, because trends rarely last forever. I choose α, β and φ by minimising one-step errors on the training data.

**Red flags:** Saying Holt handles seasonality. Using a linear trend for a multi-year horizon without checking. Confusing β with the size of the trend.

## Real world

- Charles Holt described the method in 1957. Gardner and McKenzie introduced the damped trend in 1985.
- In the M3 and M4 competitions, damped-trend exponential smoothing was a standard strong benchmark that many entries struggled to beat.
- The method is part of the ETS family in the R forecast package and in statsmodels.

## Key points

- Holt keeps a level and a trend. The forecast is l + h·b, a straight line.
- α controls the level, β controls the trend. A small β gives a stable slope.
- Damped trend multiplies the trend by φ each step. The forecast flattens at l + b·φ/(1 − φ).
- Use damped for long horizons or when unsure. Use SES when there is no trend.
