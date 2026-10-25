---
id: s11-07-kaggle-competitions
title: Kaggle forecasting competitions: Rossmann, Web Traffic, Favorita, Optiver
minutes: 20
level: intermediate
goals: [Name the main Kaggle time-series competitions and their metrics, Explain what winning solutions had in common, Compute RMSPE, SMAPE and RMSLE and see how they differ]
prereqs: [s11-06-zillow-offers-2021]
tags: [kaggle, rossmann, web-traffic, favorita, optiver, metrics]
skills: [case-studies, forecast-metrics]
---

## Warm-up

```check
{"q": "What is adverse selection?", "type": "single",
 "options": ["The other side chooses deals that are good for them, so your won deals are biased", "Selecting the best features", "Selecting the best model"],
 "answer": 0,
 "why": ["Correct.", "That is feature selection.", "That is model selection."]}
```

```check
{"q": "In M5, which model family dominated?", "type": "single",
 "options": ["Global LightGBM-based models", "Per-series ARIMA", "Naive forecasts"],
 "answer": 0,
 "why": ["Correct.", "Per-series ARIMA was not the leader.", "Naive models were benchmarks."]}
```

## Why it matters

Kaggle competitions give real data, a public leaderboard and write-ups from the winners. They are the best free school for practical forecasting. Interviewers also like to ask "what did you learn from a competition?". This lesson is a short map. The next stage (s15) has full hands-on tutorials, so here we only list the main contests and what they teach.

## The four competitions

| Competition | Data and task | Metric | What it taught |
|---|---|---|---|
| **Rossmann Store Sales** (2015) | Daily sales of about 1 100 drugstores in Germany; forecast about 6 weeks | RMSPE | Gradient boosting (XGBoost) with careful features won. A top team used neural nets with entity embeddings for store and day-of-week. |
| **Web Traffic Time Series Forecasting** (2017) | Daily page views of about 145 000 Wikipedia pages; forecast about 60 days | SMAPE | A seq2seq recurrent network won. The data is noisy and has many zeros and gaps, so the metric and the handling of missing data mattered. |
| **Corporación Favorita Grocery Sales Forecasting** (2017-18) | Store-item sales of an Ecuadorian grocery chain; forecast 16 days | NWRMSLE (weighted log error) | Promotions, holidays, store/item hierarchies, and zeros. Perishable items had more weight in the metric. |
| **Optiver Realized Volatility Prediction** (2021) | Order-book and trade data for stocks; predict volatility over the next 10 minutes | RMSPE | Feature engineering from high-frequency data, strong cross-validation, and ensembles. |

Only a few well-known points are listed. Read the winners' write-ups on Kaggle for details.

```check
{"q": "Which competition used page views of Wikipedia articles?", "type": "single",
 "options": ["Rossmann", "Web Traffic Time Series Forecasting", "Favorita", "Optiver"],
 "answer": 1,
 "why": ["Rossmann is drugstore sales.", "Correct.", "Favorita is grocery sales.", "Optiver is stock volatility."]}
```

## What winners had in common

1. **Validation that copies the test.** They built a time-based split with the same horizon and gap as the leaderboard test. A random split would fail.
2. **Features, features, features.** Lags, rolling means, calendar, holidays, promotions, price, store/item aggregates. Features known in the future (calendar, promotions) were used with care.
3. **Gradient boosting first**, neural nets as part of an ensemble.
4. **[[ensemble|Ensembling]]** of different models and seeds. Averaging is almost always a gain.
5. **Metric-aware training.** Train on log targets for RMSLE; weight rows as the metric does; treat zeros as the metric requires.
6. **Leak awareness.** Some competitions had leaks (for example in IDs or ordering). Knowing what is allowed is part of the job, and real projects must avoid leaks.

```check
{"q": "Which is the best validation for a competition with a 16-day future test?", "type": "single",
 "options": ["Random 80/20 split of rows", "The last 16 days before the test period as validation, repeated for a few earlier cutoffs", "Train error", "Shuffle days"],
 "answer": 1,
 "why": ["Random splits put the future in the training set.", "Correct: same horizon, and several cutoffs reduce noise.", "Train error is too optimistic.", "Shuffling destroys time order."]}
```

## Metrics matter

The same forecast gets different scores under different metrics. Check what a fixed absolute error of 10 units means as a percentage error for series of different size.

```chart
{"title": "A fixed error of 10 units, shown as a percent of the actual value", "x": "actual value", "height": 220,
 "series": [{"name": "percentage error (%)", "x": [10, 20, 30, 40, 50, 75, 100, 150, 200], "y": [100, 50, 33.3, 25, 20, 13.3, 10, 6.7, 5]}],
 "caption": "Percent metrics (RMSPE, SMAPE) punish errors on small values very strongly. Log metrics (RMSLE) are more balanced. Absolute metrics (MAE, RMSE) treat all values the same."}
```

- **[[RMSPE]]**: root mean of squared percentage errors. Breaks when the actual is 0 (Rossmann scored only open days).
- **[[sMAPE|SMAPE]]**: symmetric percent error. With actual = 0 and forecast = 0 the ratio is 0/0, and the competition has to define it.
- **[[RMSLE]]**: root mean squared error of `log(1 + y)`. Penalises relative error, and is good for skewed counts, such as sales.

```check
{"q": "You train a model for RMSLE. Which target transformation matches the metric?", "type": "single",
 "options": ["Train on y and predict y", "Train on log(1 + y) with squared error, then predict exp(pred) − 1", "Train on y squared", "Standardise y"],
 "answer": 1,
 "why": ["That optimises squared error on the raw scale.", "Correct: RMSE on log(1 + y) equals RMSLE on y.", "Not related.", "Standardising does not change the metric."]}
```

## Worked example

We score one forecast with three metrics, and then see what changes when one actual is 0.

```python
import numpy as np

def rmspe(y, f):
    return float(np.sqrt(np.mean(((y - f) / y) ** 2)))

def smape(y, f):
    return float(np.mean(200 * np.abs(y - f) / (np.abs(y) + np.abs(f))))

def rmsle(y, f):
    return float(np.sqrt(np.mean((np.log1p(y) - np.log1p(f)) ** 2)))

y = np.array([10.0, 50.0, 100.0, 200.0])
f = np.array([12.0, 45.0, 110.0, 190.0])
print("RMSPE:", round(rmspe(y, f), 4))
print("SMAPE:", round(smape(y, f), 2))
print("RMSLE:", round(rmsle(y, f), 4))

# Now the first actual is 0 and we forecast 2
y0 = np.array([0.0, 50.0, 100.0, 200.0])
f0 = np.array([2.0, 45.0, 110.0, 190.0])
print("RMSLE with a zero:", round(rmsle(y0, f0), 4))
print("SMAPE with a zero:", round(smape(y0, f0), 2))
with np.errstate(divide="ignore"):
    print("RMSPE with a zero:", rmspe(y0, f0))
# Output:
# RMSPE: 0.125
# SMAPE: 10.84
# RMSLE: 0.1119
# RMSLE with a zero: 0.5543
# SMAPE with a zero: 56.29
# RMSPE with a zero: inf
```

RMSPE becomes infinite when an actual is 0, and SMAPE jumps to its maximum (200) for that point. RMSLE stays finite. This is why competitions choose the metric with the data in mind.

## Common mistakes

- Tuning on the public leaderboard instead of a local time-based validation.
- Ignoring how the metric treats zeros.
- Using the private test period information in features (leakage).
- Copying competition tricks into production without checking. A leak is not a feature.
- Spending all the time on the model and not on validation and features.

## Interview lens

**Typical question:** "What did you learn from a forecasting competition?" or "How would you approach the Favorita sales task?"

**Strong answer:** I start with a validation that copies the test: same horizon, time-based, several cutoffs. I build a baseline (last week), then a gradient-boosting model with lags, rolling means, calendar, holidays, promotion and store/item features. I check how the metric treats zeros and which transform matches it, for example log1p for RMSLE. I ensemble a few models, and I watch for leaks. For production I keep what generalises: the validation scheme and the features known at prediction time.

**Red flags:** Random split. No baseline. Ignoring the metric. Saying you "won the leaderboard" without describing validation.

## Real world

These competitions are public on Kaggle with data, rules and winners' write-ups. Rossmann and Web Traffic are often cited as early examples of boosting and neural sequence models. Many later datasets build on the same ideas. Examples are M5 on Kaggle and the "Store Sales - Time Series Forecasting" getting-started contest. See stage s15 for guided notebooks.

## Key points

- Rossmann (RMSPE, boosting), Web Traffic (SMAPE, seq2seq), Favorita (weighted log error, promotions and hierarchy), Optiver (volatility, RMSPE).
- Winners share: time-based validation, strong features, boosting, ensembles, metric-aware training.
- Percent metrics break on zeros; log metrics are more stable.
- Match the training transform to the metric.
- Competition tricks are not always production practice. Avoid leaks.
