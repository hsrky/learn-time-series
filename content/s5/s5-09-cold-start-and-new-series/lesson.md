---
id: s5-09-cold-start-and-new-series
title: Cold start: forecasting new series
minutes: 25
level: intermediate
goals: [Explain the cold-start problem, Forecast a new series from similar series and from a hierarchy, Blend a prior with the growing history and mention foundation models as an option]
prereqs: [s5-06-global-vs-local-models, s5-08-exogenous-and-known-future]
tags: [cold-start, new-series, hierarchy, analogs, foundation-models]
skills: [scale, baseline-first]
---
## Warm-up
```check
{"q": "Why can a global model forecast a product that has only 2 weeks of history?", "type": "single",
 "options": ["It learned patterns from many other series", "It ignores the data of the new product", "It uses future sales"],
 "answer": 0,
 "why": ["Correct: shared patterns come from older series; static features describe the new one.", "It does use the new product's data and features.", "Future sales are not available."]}
```

```check
{"q": "You standardize a new series with only 3 points. What is risky?", "type": "single",
 "options": ["The mean and standard deviation are very noisy", "Nothing", "The series becomes longer"],
 "answer": 0,
 "why": ["Correct: 3 points give unstable statistics. Use a prior or a scale from similar series.", "Short series make the scaler unstable.", "Scaling does not add points."]}
```

## Why it matters
Every month a retailer adds new products. A bike-share company opens new stations. A cloud provider starts new services. These **new series** have no history or very little. The business still needs a forecast on day one: how much stock to order, how many bikes to move. This is the **[[cold start|cold-start problem]]**. Classical local methods fail here, because they need data. The solutions use data from other series.

## Idea 1: similar-series prior (analogs)
Find older series that are **like** ([[analog forecasting]]) the new one (same category, price band, brand, region). Look at how they behaved **since their own launch**. Then borrow their shape.

Steps:
1. Align series by **age** (days since launch), not by calendar date. A product launched in June and one launched in November can then be compared.
2. Normalize each analog by its own level, for example by the mean of its first `L` days.
3. Average the normalized future (ages `L … L+h−1`) of the best matches.
4. Multiply by the level of the new series, for example the mean of its first `L` days.

Example: analogs sell 10, 14, 18 in their first 3 days and then 20, 20. The normalized shape (divide by the mean 14) after day 3 is 1.43, 1.43. A new product sells 5, 7, 9 (mean 7). Forecast = 7 × 1.43 = 10, 10.

```check
{"q": "An analog sold 10, 14, 18 on days 1 to 3 (mean 14) and then 21 on day 4. A new product sold 5, 7, 9 (mean 7). Forecast for day 4 with the analog method?", "type": "numeric",
 "answer": 10.5, "tol": 0.001,
 "why": "Shape for day 4 = 21 / 14 = 1.5. Forecast = 7 × 1.5 = 10.5."}
```

## Idea 2: use the hierarchy
Often the new series belongs to a group: the product to a category, the station to a city. The **parent** series has plenty of data. Forecast the parent and give the new child a **share** of it ([[top-down forecast|top-down]]). As the child collects data, replace the share with its own history.

A simple way to move from the prior to the own data is a **blend**:

`forecast = w × own + (1 − w) × prior`, with `w = n / (n + k)`

- `n` is the number of observed points of the new series.
- `k` is a constant (for example 14). A larger `k` trusts the prior longer.
- At `n = 0` the weight on own data is 0. At `n = k` it is 0.5. For a long history, `w` is close to 1.

```check
{"q": "w = n / (n + k) with k = 10. After n = 30 observed points, what is w?", "type": "numeric",
 "answer": 0.75, "tol": 0.001,
 "why": "30 / (30 + 10) = 0.75. The own data now has 75% of the weight."}
```

## Idea 3: global model with features, and foundation models
- A **global model** with **static features** (category, price, size, region) can forecast a new series, because it never needed the series id: it uses the attributes. Add the series **age** as a feature to learn launch curves.
- **[[foundation model|Foundation models]]** (Chronos, TimesFM, Moirai and others) are pretrained on huge collections of series. In **[[zero-shot]]** use they forecast from a short context, without training on the new series. They are a good baseline when a series has some points. With zero history they cannot help. Compare them with simple analog and seasonal baselines.
- **Judgement from planners:** for a launch with no data, business input (a plan or a launch target) is a prior too. Record it and compare it with the model.

| Situation | Option |
|---|---|
| No history, rich attributes | Global model on attributes + age; analogs; planner input |
| A few points | Analog shape × own level, blended with own history |
| 10+ points | Add a foundation model or the global model with own lags |
| New series in a stable hierarchy | Top-down share of the parent |

```check
{"q": "A product has zero sales history but a known category and price. Which method can still produce a forecast?", "type": "single",
 "options": ["ARIMA on the product", "A global model using category and price, or analogs", "Seasonal naive of the product"],
 "answer": 1,
 "why": ["ARIMA needs history.", "Correct: use features and similar products.", "Seasonal naive needs at least one season of own history."]}
```

## Evaluate cold start separately
Overall accuracy hides cold-start errors, because new series are a small share of the rows. Evaluate **by age**: report the error for series in their first 7 days, 8–28 days, and older. Do this in a backtest where the new series really appear later, so that the model does not see their first days in training.

```chart
{"title": "Blend weight on own data grows with history (k = 14)", "x": "observed points n", "height": 200,
 "series": [{"name": "w = n / (n + 14)", "x": [0, 3, 7, 14, 28, 56, 112], "y": [0, 0.18, 0.33, 0.5, 0.67, 0.8, 0.89]}],
 "caption": "At 14 points, own history and prior have equal weight. At 112 points, the prior has only 11%."}
```

## Worked example
Six older products have the same launch curve (a ramp up) with different levels. A new product has 5 days of history. We forecast days 6 to 10 with (a) the mean of the 5 days, (b) the analog shape method using the 3 nearest analogs.

```python
import numpy as np

rng = np.random.default_rng(2)
ages = np.arange(10)
shape = 1 - 0.7 * np.exp(-ages / 3.0)                  # launch ramp, goes from 0.3 to about 1
levels = [30, 80, 55, 120, 40, 65]
analogs = [lv * shape * (1 + rng.normal(0, 0.05, 10)) for lv in levels]

new_level = 50
new_full = new_level * shape * (1 + rng.normal(0, 0.05, 10))
hist, future = new_full[:5], new_full[5:]
L, h = 5, 5

# distance between the shapes of the first L days (each divided by its own mean)
dist = [np.abs(hist / hist.mean() - a[:L] / a[:L].mean()).mean() for a in analogs]
best = np.argsort(dist)[:3]
shape_fc = np.mean([a[L:L + h] / a[:L].mean() for a in (analogs[i] for i in best)], axis=0)
fc_analog = shape_fc * hist.mean()                     # scale to the new level
fc_mean = np.full(h, hist.mean())                      # naive: mean of the 5 days

print("history   :", hist.round(1))
print("truth     :", future.round(1))
print("analog fc :", fc_analog.round(1))
print("mean fc   :", fc_mean.round(1))
print("MAE analog:", round(np.abs(future - fc_analog).mean(), 2))
print("MAE mean  :", round(np.abs(future - fc_mean).mean(), 2))
# Output:
# history   : [15.5 24.7 31.7 36.9 42.1]
# truth     : [41.1 41.8 40.9 50.4 48.4]
# analog fc : [44.1 47.1 46.8 46.4 46.4]
# mean fc   : [30.2 30.2 30.2 30.2 30.2]
# MAE analog: 4.06
# MAE mean  : 14.35
```

The mean of the first days is too low, because the product is still ramping up. The analog method knows the ramp and gives a much smaller error.

## Common mistakes
- Using calendar dates to compare launches, instead of age since launch.
- Fitting a per-series scaler on 2 or 3 points.
- Picking analogs by the level of sales only. Match the shape and the attributes.
- Evaluating cold start only inside the overall average.
- Letting the model see the new product's first weeks in training and then calling it "cold start".
- Ignoring business plans (launch targets) as a baseline.

## Interview lens
**Typical question:** "A new product launches tomorrow. How do you forecast it?"

**Strong answer:** There is no history, so I borrow information. I align older products by age and find similar ones by category, price and region. I use their normalized launch curves and scale them to a planned or early level. In parallel I use a global model with static features and age. As data arrives, I blend the prior with the new series using a weight like n / (n + k). A parent in the hierarchy can supply a top-down share. For short contexts a pretrained foundation model is another baseline. I evaluate the error by series age so that cold start is visible.

**Red flags:** "Wait for 2 years of data"; "run ARIMA"; a global model with series id as the only identity; ignoring the evaluation of new series separately.

## Real world
- Zero-shot foundation models such as Chronos and TimesFM forecast from a short context without per-series training. They are often used as a baseline for new series.
- Retail forecasting guides describe "like-item" or "analog" forecasting for product launches, and top-down allocation of a category forecast to new items.
- The M5 competition data included items that started selling late in the period; models needed a way to handle items with short history.

## Key points
- Cold start means a new series with no or little history.
- Borrow information: analogs aligned by age, parent series in the hierarchy, global models with static features and age.
- Blend the prior with the own history using `w = n / (n + k)`.
- Foundation models can forecast from short context but still need a baseline comparison.
- Evaluate by series age.
