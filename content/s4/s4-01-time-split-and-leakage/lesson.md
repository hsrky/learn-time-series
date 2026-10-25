---
id: s4-01-time-split-and-leakage
title: Time-based split and data leakage
minutes: 25
level: beginner
goals: [Split a series into train and test by time, Name four kinds of data leakage, Fit scalers on the training part only]
prereqs: []
tags: [evaluation, leakage, split]
skills: [leakage, baseline-first]
---
## Warm-up
Two quick questions. Think first, then answer.

```check
{"q": "A forecast is a statement about which part of time?", "type": "single",
 "options": ["The past", "The future", "Only the present moment"],
 "answer": 1,
 "why": ["We already know the past. We do not need to forecast it.", "Correct: a forecast says something about times that have not happened yet.", "A forecast always looks ahead of the last known time."]}
```

```check
{"q": "The naive forecast repeats the last known value. For the series 4, 6, 5, 7, what is the naive forecast for the next step?", "type": "numeric",
 "answer": 7, "tol": 0.001,
 "why": "The last known value is 7, so the naive forecast is 7."}
```

## Why it matters
A team builds a sales model. In testing, the error is tiny. In production, the error is five times bigger. What went wrong? Often the test was not honest. The model **saw the future** during training. This mistake is called [[data leakage]]. It is the most common reason a time-series project fails in review. Interviewers ask about it in almost every loop. In this lesson you learn to split data by time and to find leaks.

## Train and test must follow time
You want to know how a model will work on **new** data. So you hide part of the data. You train on the first part. You test on the last part.

- The first part is the [[training set]].
- The last part is the [[test set]].
- The time that separates them is the [[cutoff]].

Example: 120 days of data. Train on days 1 to 90. Test on days 91 to 120. In real life you also stand at day 90 and look ahead. The test copies real life.

```widget
{"name": "train-test-split", "params": {}}
```

```check
{"q": "You have 200 daily rows. You use the last 20% as the test set. Which rows are in the test set?", "type": "single",
 "options": ["20 random rows", "The last 40 rows", "The first 40 rows"],
 "answer": 1,
 "why": ["Random rows would mix past and future.", "Correct: 20% of 200 is 40, and the test set is the newest part.", "The first rows are the oldest. They belong to training."]}
```

## Why a random split is wrong
A random split puts some future rows in the training set. Look at this small series: 10, 11, 12, **?**, 14, 15. The missing value is easy to guess. It lies between 12 and 14. A model that sees both sides is **interpolating**. It is not forecasting.

In real life you never see day 14 when you predict day 13. So a random split gives a score that is too good. We call this **[[look-ahead bias]]**: the model uses information from after the prediction time.

A random split has a second problem. Neighbouring days look alike ([[autocorrelation]]). A test row almost copies a training row next to it. The test is no longer a new case.

```chart
{"title": "Random split: test points (dots) sit between training points", "x": "day", "height": 220,
 "series": [
   {"name": "series", "gen": [["trend", {"slope": 0.5, "start": 10}], ["noise", {"sd": 1.0}]], "n": 60, "seed": 5},
   {"name": "trend", "gen": [["trend", {"slope": 0.5, "start": 10}]], "n": 60, "dash": true}
 ],
 "marks": [{"x": 45, "label": "time cutoff"}],
 "caption": "With a time cutoff, every test day comes after day 45. With a random split, test days hide between training days."}
```

```check
{"q": "Why does a random split give a score that is too good for forecasting?", "type": "single",
 "options": ["The test set becomes too small", "The model can learn from days after the test day", "Random numbers are not reproducible"],
 "answer": 1,
 "why": ["The size can be the same. The problem is the order.", "Correct: training rows from the future help the model guess the test rows.", "You can fix the seed. The problem is not the randomness itself."]}
```

## Four kinds of leakage
Leakage means information enters training that you will not have at prediction time. Learn these four.

1. **Random split.** Future rows are in training (see above).
2. **Full-data statistics.** You compute the mean or standard deviation on all rows, then scale. The test rows then shape the scaler.
3. **Future covariates.** A feature is only known later. Example: you predict sales for Monday and use the *actual* weather of Monday. At prediction time you only have a weather *forecast*.
4. **Rolling features without a shift.** A 7-day mean that includes today contains today's target. You must shift the feature by one step.

```check
{"q": "You predict tomorrow's demand. Which feature is a leak?", "type": "single",
 "options": ["Demand 7 days ago", "Tomorrow's actual price, set by a rule you do not know yet", "Day of week of tomorrow"],
 "answer": 1,
 "why": ["This value is already known today. It is safe.", "Correct: if the price is not known when you predict, using it leaks the future.", "The calendar is known in advance. It is safe."]}
```

## Fit on train, apply to test
Scaling means turning values into a common range. A common scaler is [[standardization]]: `z = (x − mean) / sd`.

- `x` is a value.
- `mean` is the average of the **training** values.
- `sd` is the standard deviation of the **training** values.

The rule: **fit** (compute mean and sd) on the training set only. Then **apply** the same numbers to the test set. The same rule holds for every learned step: imputation, encoders, feature selection, even choosing hyperparameters.

If the series has a trend, the test values are large. A scaler fitted on all data then shifts toward the test. The model gets a hint about the future level.

```check
{"q": "Train mean = 50, train sd = 10. A test value is 80. What is its standardized value using the correct method?", "type": "numeric",
 "answer": 3, "tol": 0.001,
 "why": "(80 - 50) / 10 = 3. We use the training mean and sd, not the test statistics."}
```

## Gap and size of the test
Sometimes you add a **gap** between train and test. Example: features use the last 7 days, or labels need 3 days to arrive. Rows near the cutoff then overlap. A gap (also called an [[embargo]]) removes these rows. You learn more in the next lesson.

Make the test set as long as the real forecast **[[horizon]]**, the number of steps ahead you must predict. If you must predict 28 days, test on at least 28 days. One short test window can be lucky. Several windows are better.

```check
{"q": "A label for day t is the sales sum of days t to t+6. You train up to day 100. What should you do for the first test day?", "type": "single",
 "options": ["Start the test on day 101", "Leave a gap so no training label uses test days", "Shuffle days 95 to 105"],
 "answer": 1,
 "why": ["The label of day 100 includes days 101 to 106, which are test days. That is a leak.", "Correct: the training label of day 100 covers days up to 106, so the test should start after that.", "Shuffling mixes past and future. It makes the leak worse."]}
```

## Worked example
We build a trending series. Then we compare an honest test with a random-split test and with a leaky scaler.

```python
import numpy as np
import pandas as pd

rng = np.random.default_rng(0)
t = np.arange(120)
s = pd.Series(10 + 0.5 * t + rng.normal(0, 1, 120),
              index=pd.date_range("2024-01-01", periods=120, freq="D"))

# 1) Honest split by time: train = first 90 days, test = last 30 days.
cut = 90
train, test = s.iloc[:cut], s.iloc[cut:]
# Naive forecast: repeat the last training value for every test day.
naive = np.full(len(test), train.iloc[-1])
mae_time = np.abs(test.values - naive).mean()

# 2) Random split: predict each test day by the mean of its two neighbours.
#    This is only possible because the neighbours come from the future.
test_idx = rng.choice(np.arange(1, 119), size=30, replace=False)
interp = (s.values[test_idx - 1] + s.values[test_idx + 1]) / 2
mae_random = np.abs(s.values[test_idx] - interp).mean()

# 3) Scaler leak: mean of all data versus mean of the training data.
print("train mean:", round(train.mean(), 2))
print("all-data mean:", round(s.mean(), 2))
print("MAE honest time split:", round(mae_time, 2))
print("MAE random split:", round(mae_random, 2))
# Output:
# train mean: 32.36
# all-data mean: 39.83
# MAE honest time split: 6.22
# MAE random split: 0.84
```

The random split looks about seven times better. But it is a trick: the model saw both neighbours of every test day. The all-data mean is also higher than the train mean, because the trend goes up. A scaler fitted on all data would leak that.

## Common mistakes
- Using `train_test_split(shuffle=True)` on a time series. Always keep the order.
- Scaling or imputing the full table first, then splitting.
- Picking the best model by looking at the test score many times. The test set then becomes training data for *you*. Keep a final untouched part.
- Forgetting that features such as weather or price may not be known in advance.
- Using a test set that is shorter than the forecast horizon.

## Interview lens
**Typical question:** "You built a demand model with 95% accuracy. How do you check it is not leaking?"

**Strong answer:** First I check the split. It must be by time, with the test set after the training set. Then I check every feature. I ask: "Is this value known at the moment I predict?" I make sure scalers and encoders are fitted on training data only. I shift rolling features by one step. Finally I compare with a [[naive forecast]]. If my model beats naive by a huge margin, I suspect a leak and I look at the feature importance for a suspicious column.

**Red flags:** saying "I used a random 80/20 split"; scaling before splitting; not knowing the word look-ahead bias; never comparing with a baseline.

## Real world
- Kaggle time-series competitions usually split by date. The private test period comes after the training data. People who leak the future may rank high on the public board and then fall on the private one.
- The scikit-learn library has `TimeSeriesSplit` because plain `KFold` is wrong for ordered data.
- The M5 forecasting competition (Walmart data) asked for forecasts of a period after the training data. The score came only from that hidden future.

## Key points
- Split by **time**: train on the past, test on the future.
- A random split leaks the future and gives scores that are too good.
- Four leaks: random split, full-data statistics, future covariates, unshifted rolling features.
- Fit every learned step on the training set only, then apply it to the test set.
- Compare with a naive forecast. A result that is too good is a warning sign.
