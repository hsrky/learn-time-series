---
id: s3-01-baselines
title: Baselines: always start here
minutes: 25
level: beginner
goals: [Compute the mean, naive, seasonal naive and drift forecasts, Choose the baseline that fits the pattern of the data, Measure the lift of a model against a baseline, Explain why you always build a baseline first]
prereqs: [s2-01-white-noise-random-walk]
tags: [baseline, naive, seasonal-naive, drift]
skills: [baseline-first, metrics]
---

## Warm-up

```check
{"q": "The best forecast of a random walk without drift is...", "type": "single",
 "options": ["The last value", "The mean of all values", "Zero"],
 "answer": 0,
 "why": ["Correct: future shocks have mean zero, so the last value is the best guess.", "The mean ignores where the walk is now.", "A walk is not centred on zero."]}
```

```check
{"q": "What does 'stationary' mean?", "type": "single",
 "options": ["Mean and spread do not change over time", "The series has no noise", "The series is always positive"],
 "answer": 0,
 "why": ["Correct: stable mean, stable variance and stable autocorrelation.", "Stationary series can be noisy. White noise is stationary.", "Sign does not matter."]}
```

## Why it matters

A team spends three months on a complex neural network. Then someone tests the forecast "same as last week". The simple forecast is almost as good. This story is common. A **[[baseline]]** is a very simple forecast. A new model must **beat the baseline** to be worth its cost. Without a baseline, the number "MAE = 12" means nothing. With a baseline, "12 versus 20 for the baseline" is a clear result.

## The four classic baselines

Take the history y(1), ..., y(n) and a horizon h (how many steps ahead).

| Method | Forecast for y(n+h) | Idea |
|---|---|---|
| **Mean** | average of all history | Nothing changes. Best for noise around a fixed level. |
| **Naive** | y(n), the last value | Tomorrow is like today. Best for a random walk. |
| **Seasonal naive** | y(n+h−m·k), the value one season ago | Same weekday as last week. Best for strong seasons. |
| **Drift** | y(n) + h·(y(n)−y(1))/(n−1) | Continue the average change. Best for a steady trend. |

Here m is the season length (7 for weekly data on daily steps). The number k is the smallest whole number that gives an index inside the history, so k = ⌈h/m⌉.

Numbers: history 10, 12, 14, 13. Mean = 12.25. Naive = 13. Drift: slope = (13 − 10)/3 = 1, so h = 1 gives 14 and h = 2 gives 15.

```check
{"q": "History: 10, 12, 14, 13. What is the drift forecast for h = 3?", "type": "numeric",
 "answer": 16, "tol": 0.01,
 "why": "Slope = (13 - 10) / 3 = 1. Forecast = 13 + 3 * 1 = 16."}
```

## Seasonal naive in detail

Data with m = 4: 10, 20, 30, 40, 12, 22, 32, 42. The next 4 values are copies of the last season: 12, 22, 32, 42. For h = 5..8 you copy the same season again: 12, 22, 32, 42.

This is very strong for data with a clear repeating pattern. Examples are daily sales with a weekly cycle and hourly load with a daily cycle. In many real tasks it is hard to beat by a large margin.

```chart
{"title": "Seasonal naive repeats the last week (dashed). History is the solid line.", "x": "day", "height": 230,
 "series": [
  {"name": "actual (history + test)", "y": [50.3, 55.8, 57.8, 50.7, 50.4, 45.4, 45.1, 53.3, 59.1, 59.7, 57.9, 49.4, 45.3, 46.5, 54.9, 60.6, 63.4, 57.7, 52.1, 46.6, 51.0, 56.6, 63.4, 65.3, 59.2, 55.2, 53.1, 49.4, 55.8, 62.7, 68.1, 63.0, 57.7, 53.2, 54.3, 60.9, 66.8, 70.2, 63.2, 57.6, 54.6, 58.7]},
  {"name": "seasonal naive forecast", "dash": true, "x": [28,29,30,31,32,33,34,35,36,37,38,39,40,41], "y": [56.6, 63.4, 65.3, 59.2, 55.2, 53.1, 49.4, 56.6, 63.4, 65.3, 59.2, 55.2, 53.1, 49.4]},
  {"name": "naive forecast", "dash": true, "x": [28,29,30,31,32,33,34,35,36,37,38,39,40,41], "y": [49.4, 49.4, 49.4, 49.4, 49.4, 49.4, 49.4, 49.4, 49.4, 49.4, 49.4, 49.4, 49.4, 49.4]}
 ],
 "marks": [{"x": 28, "label": "forecast starts"}],
 "caption": "The flat naive line misses the weekly shape. The seasonal naive line follows it."}
```

```check
{"q": "Hourly electricity load has a strong daily cycle. Which baseline do you try first?", "type": "single",
 "options": ["Seasonal naive with m = 24", "Mean of all history", "Drift"],
 "answer": 0,
 "why": ["Correct: copy the same hour from yesterday. m = 24 for hourly data with a daily cycle.", "The mean ignores the daily shape.", "Drift follows a straight line, not a cycle."]}
```

## Measure the lift

Compare a model with a baseline on the **same test period** with the same metric. A simple score:

skill = 1 − error_model / error_baseline

- skill > 0: the model is better than the baseline. 0.2 means 20% lower error.
- skill = 0: same as the baseline.
- skill < 0: the model is worse. Do not ship it.

Numbers: baseline MAE = 10, model MAE = 8. Skill = 1 − 8/10 = 0.2.

Always compare to the **right** baseline. For weekly data, the naive baseline is too weak. Use seasonal naive.

```check
{"q": "Baseline MAE = 5.0 and your model MAE = 6.0. What is the skill score?", "type": "numeric",
 "answer": -0.2, "tol": 0.001,
 "why": "1 - 6 / 5 = -0.2. A negative skill means the model is worse than the baseline."}
```

## Worked example

We build a daily series with a weekly pattern, hold out the last 14 days, and compare the four baselines.

```python
import numpy as np

rng = np.random.default_rng(2)
t = np.arange(42)
y = 50 + 0.3 * t + 8 * np.sin(2 * np.pi * t / 7) + rng.normal(0, 1.5, 42)
train, test = y[:28], y[28:]          # test = last 14 days, never used for fitting
h = np.arange(1, 15)                  # horizons 1..14
m = 7                                 # season length

forecasts = {
    "mean": np.full(14, train.mean()),
    "naive": np.full(14, train[-1]),
    "seasonal naive": train[len(train) - m + (h - 1) % m],   # value m*k steps back
    "drift": train[-1] + h * (train[-1] - train[0]) / (len(train) - 1),
}

def mae(a, f):
    return np.mean(np.abs(a - f))

for name, f in forecasts.items():
    print(f"{name:<15} MAE = {mae(test, f):6.2f}")
skill = 1 - mae(test, forecasts["seasonal naive"]) / mae(test, forecasts["naive"])
print("skill of seasonal naive vs naive:", round(skill, 2))
# Output:
# mean            MAE =   6.51
# naive           MAE =  11.09
# seasonal naive  MAE =   3.25
# drift           MAE =  11.34
# skill of seasonal naive vs naive: 0.71
```

The seasonal naive baseline has by far the lowest error. Any new model for this series must beat 3.25.

## Common mistakes

- Skipping the baseline, or using a weak one (naive on strongly seasonal data).
- Computing the baseline on a different period or data than the model.
- Fitting the mean on the whole data including the test period (leakage).
- Using the wrong season length m.
- Reporting only your model's error, with no baseline next to it.

## Interview lens

**Typical question:** "You built a gradient boosting model for demand. How do you know it is good?"

**Strong answer:** I compare it with simple baselines on a time-based holdout with several forecast origins. I use naive and seasonal naive, and the drift if there is a trend. I report the error of each and the skill score of the model against the best baseline. If the model gains only a few percent but costs much more to run and maintain, I would keep the simple method. I also check the gain by horizon and by segment.

**Red flags:** No baseline at all. A baseline that is too weak for the data. Evaluating on random splits. Judging a model by R² or by training error.

## Real world

- In the M4 forecasting competition (2018), the organisers used the naive and seasonal naive methods as benchmarks. Entries were scored relative to them.
- Open-source libraries such as statsforecast include naive and seasonal naive models. A good forecaster always checks them first.

## Key points

- A baseline is a very simple forecast: mean, naive, seasonal naive or drift.
- Pick the one that fits the pattern: noise → mean, random walk → naive, trend → drift, season → seasonal naive.
- Skill = 1 − error_model / error_baseline. Positive means the model adds value.
- Always build the baseline first and always report it beside your model.
