---
id: s15-02-store-sales-baseline-validation
title: Store Sales, part 1 - goal, data tour, baseline and validation
minutes: 45
level: intermediate
goals: [Explain the Store Sales task and the RMSLE metric, Explore the files and find the traps in the data, Build a time-based validation that copies the test period, Make a seasonal naive baseline and your first submission]
prereqs: [s15-01-how-kaggle-works]
tags: [kaggle, store-sales, favorita, RMSLE, baseline, validation]
skills: [baseline-first, backtest, metrics]
---

## Warm-up

```check
{"q": "What is the main idea of a seasonal naive forecast?", "type": "single", "options": ["Repeat the value from the same point in the last season", "Predict zero", "Use the global mean", "Use a neural network"], "answer": 0, "why": ["Correct.", "No.", "No.", "No."]}
```
```check
{"q": "Why use shift before a rolling mean when building a feature?", "type": "single", "options": ["To make it faster", "So the window does not include the current or unknown days", "To add noise", "To sort the data"], "answer": 1, "why": ["No.", "Correct.", "No.", "No."]}
```

## Why it matters

*Store Sales – Time Series Forecasting* is the best first Kaggle forecasting project. It is a "Getting Started" competition. It has no prize and no deadline, so you can learn at your own speed. The data comes from Corporación Favorita, a large grocery retailer in Ecuador. You forecast the sales of thousands of product families in many stores. It has all the real problems: many series, holidays, promotions, missing days, and zeros. This is part 1 of 2. In part 1 you understand the task and build a strong baseline. In [[lesson:s15-03-store-sales-features-model-submission]] you build features and a LightGBM model.

Work in a Kaggle notebook: open the competition page, press "Code", then "New Notebook". The data is attached under `/kaggle/input/store-sales-time-series-forecasting/`.

## Step 1: goal and metric

**Goal.** Predict `sales` for every store and product family. The test period is the **16 days** after the end of the training data. There are 54 stores and 33 families, so 1,782 series.

**Metric: RMSLE.** Root mean squared logarithmic error:

`RMSLE = sqrt( mean( (log(1 + prediction) − log(1 + actual))² ) )`

- `log(1 + x)` is `np.log1p(x)`. It is 0 for 0 sales, so zero sales are allowed.
- It measures **relative** error. Missing 10 units when the actual is 10 is as bad as missing 1000 when the actual is 1000.
- Over-forecasts and under-forecasts are punished almost the same on the log scale.
- Lower is better. A perfect score is 0.

A useful trick: train a model on `y = log1p(sales)` with a normal squared-error loss. Then its RMSE on `y` **is** the RMSLE. You optimise the metric directly.

```check
{"q": "Actual sales are 0 and your forecast is 3. What is the error term inside RMSLE for this row (use natural log)?", "type": "numeric",
 "answer": 1.386, "tol": 0.01,
 "why": "log(1 + 3) − log(1 + 0) = log 4 − 0 = 1.386. Squared, it is 1.92."}
```

## Step 2: files and data tour

| File | Columns | Use |
|---|---|---|
| `train.csv` | `id, date, store_nbr, family, sales, onpromotion` | History to learn from |
| `test.csv` | `id, date, store_nbr, family, onpromotion` | Rows to predict (no sales) |
| `stores.csv` | `store_nbr, city, state, type, cluster` | Store details |
| `oil.csv` | `date, dcoilwtico` | Daily oil price (Ecuador's economy depends on oil) |
| `holidays_events.csv` | `date, type, locale, locale_name, description, transferred` | Holidays and events |
| `transactions.csv` | `date, store_nbr, transactions` | Customer visits per store and day, **train period only** |
| `sample_submission.csv` | `id, sales` | The format to upload |

`onpromotion` counts how many items of the family were on promotion that day. It exists in the test file, so it is a **known-future** feature.

```notebook
# Run this in a Kaggle notebook (Data: Store Sales - Time Series Forecasting)
import numpy as np
import pandas as pd

DATA = "/kaggle/input/store-sales-time-series-forecasting/"
train = pd.read_csv(DATA + "train.csv", parse_dates=["date"])
test = pd.read_csv(DATA + "test.csv", parse_dates=["date"])
stores = pd.read_csv(DATA + "stores.csv")
oil = pd.read_csv(DATA + "oil.csv", parse_dates=["date"])
holidays = pd.read_csv(DATA + "holidays_events.csv", parse_dates=["date"])
transactions = pd.read_csv(DATA + "transactions.csv", parse_dates=["date"])

print(train.shape, test.shape)
print(train.head())
```

## Step 2b: look at the data

Now look at the data like a detective. Ask five questions: What dates? How many series? Which days are missing? How many zeros? What is the level and trend?

```notebook
print("train dates:", train["date"].min().date(), "to", train["date"].max().date())
print("test dates: ", test["date"].min().date(), "to", test["date"].max().date())
print("stores:", train["store_nbr"].nunique(), "| families:", train["family"].nunique())
print("series (store x family):", train.groupby(["store_nbr", "family"]).ngroups)

# Which calendar days are missing from the training data?
all_days = pd.date_range(train["date"].min(), train["date"].max(), freq="D")
missing = all_days.difference(pd.DatetimeIndex(train["date"].unique()))
print("missing days:", [d.strftime("%Y-%m-%d") for d in missing])

# Share of zero sales by family (some families sell rarely)
zero_share = (train["sales"] == 0).groupby(train["family"]).mean().sort_values(ascending=False)
print(zero_share.head(8).round(2))

# Average total sales per day, by month
daily = train.groupby("date")["sales"].sum()
print(daily.resample("MS").mean().tail(6).round(0))
```

What you should find (check the output on the real data):

- The training data ends on **2017-08-15** and the test period is the following **16 days**.
- Some calendar days are **missing**, for example 25 December in each year. They have no rows at all.
- Many series have long runs of **zeros**. This is common at the start (stores that had not opened yet) and for rare families.
- Sales have a **weekly pattern**, a long-term **trend**, and spikes around holidays and paydays. (In Ecuador, public-sector wages are paid on the 15th and the last day of the month.)

```check
{"q": "A store has zero sales for all families during its first 300 days in the data. What is the most likely reason, and what should you do?", "type": "single",
 "options": ["The store sold nothing for 300 days by choice; keep the rows", "The store was not open yet; consider dropping those early rows from training", "It is a data error in the test file", "Zero sales help the model; add more zeros"],
 "answer": 1,
 "why": ["A shop does not run for 300 days with no sales. Check opening dates.", "Correct: stores that open later show zeros before opening. Those rows teach the wrong pattern.", "The test file has no sales.", "They add noise."]}
```

## Step 3: validation scheme

The test period is the 16 days after the last training day. Copy this exactly.

- **Validation set:** the last 16 days of the training data.
- **Fit set:** all days before that.
- Score with RMSLE. Never score with a random split.

For a more stable estimate, repeat with one or two earlier windows of 16 days. This chapter uses one window to stay simple.

```widget
{"name": "walk-forward", "params": {}}
```

```notebook
H = 16                                         # length of the test period in days
last_day = train["date"].max()
valid_start = last_day - pd.Timedelta(days=H - 1)
fit = train[train["date"] < valid_start]
valid = train[train["date"] >= valid_start]
print("fit until", fit["date"].max().date(),
      "| validation", valid["date"].min().date(), "to", valid["date"].max().date())

def rmsle(y_true, y_pred):
    y_pred = np.clip(y_pred, 0, None)          # negative sales make no sense
    return float(np.sqrt(np.mean((np.log1p(y_pred) - np.log1p(y_true)) ** 2)))
```

```check
{"q": "Why do we use the LAST 16 days of the training data as validation and not 16 random days?", "type": "single",
 "options": ["It is faster", "It copies the test: future days, with training only on the past", "Random days are not allowed in pandas", "The last days have no noise"],
 "answer": 1,
 "why": ["Speed is not the reason.", "Correct: neighbouring days would leak information in a random split.", "Pandas allows it; it would be wrong for time series.", "They are as noisy as other days."]}
```

## Step 4: baselines

Always start with simple rules. They are fast, hard to beat, and tell you how good a model must be.

1. **All zeros.** The worst reasonable baseline. It shows the scale of the metric.
2. **Mean of the last 14 days** per series.
3. **Seasonal naive.** For each series, repeat the last 7 days. Monday is predicted by last Monday, and so on. This uses the weekly pattern.

```chart
{"title": "Seasonal naive: the last week is repeated forward (period 7)", "x": "day", "height": 230,
 "series": [
   {"name": "sales (history + next 16 days)", "gen": [["trend", {"slope": 0.2, "start": 100}], ["season", {"period": 7, "amp": 20}], ["noise", {"sd": 3}]], "n": 70, "seed": 4},
   {"name": "trend only", "gen": [["trend", {"slope": 0.2, "start": 100}]], "n": 70, "dash": true}
 ],
 "marks": [{"x": 54, "label": "forecast starts"}],
 "caption": "The weekly wave repeats. Seasonal naive copies the last wave and ignores the trend and the noise."}
```

```notebook
def seasonal_naive(fit, targets, season=7):
    """For each target row, take the sales of the same weekday in the last `season` days of `fit`."""
    last = fit["date"].max()
    t = targets[["id", "store_nbr", "family", "date"]].copy()
    steps = np.ceil((t["date"] - last).dt.days / season).astype(int)      # how many weeks back
    t["src_date"] = t["date"] - pd.to_timedelta(steps * season, unit="D")
    src = fit[["store_nbr", "family", "date", "sales"]].rename(columns={"date": "src_date"})
    t = t.merge(src, on=["store_nbr", "family", "src_date"], how="left")
    t["sales"] = t["sales"].fillna(0.0)
    return t[["id", "sales"]]

# Baseline 1: all zeros
print("RMSLE zeros        :", round(rmsle(valid["sales"].values, np.zeros(len(valid))), 4))

# Baseline 2: mean of the last 14 days of each series
last14 = fit[fit["date"] >= fit["date"].max() - pd.Timedelta(days=13)]
mean14 = last14.groupby(["store_nbr", "family"])["sales"].mean().rename("pred").reset_index()
v = valid.merge(mean14, on=["store_nbr", "family"], how="left").fillna({"pred": 0.0})
print("RMSLE mean last 14 :", round(rmsle(v["sales"].values, v["pred"].values), 4))

# Baseline 3: seasonal naive
pred = seasonal_naive(fit, valid)
v = valid[["id", "sales"]].merge(pred, on="id", suffixes=("_true", "_pred"))
print("RMSLE seasonal naive:", round(rmsle(v["sales_true"].values, v["sales_pred"].values), 4))
```

Write down the three scores. Your LightGBM model in part 2 must beat the best one by a clear margin. The mini problem [[problem:rmsle-seasonal-naive-submission]] makes you write these two functions yourself.

## Step 5: your first submission

Use all training data (not only `fit`) to forecast the real test rows. The file needs the columns `id` and `sales`.

```notebook
sub = seasonal_naive(train, test)               # uses the last 7 days up to 2017-08-15
sub.to_csv("submission.csv", index=False)
print(sub.shape, sub["sales"].describe().round(2).to_dict())
```

Click "Save Version", wait for the run to finish, and press "Submit to Competition". Your public score should be close to your validation score. If it is very different, check the validation setup.

## Worked example

A tiny, runnable version in the browser: three stores, two families, 28 days of data, and a 7-day test. We build the seasonal naive forecast and score it with RMSLE on a validation week.

```python
import numpy as np
import pandas as pd

rng = np.random.default_rng(0)
days = pd.date_range("2024-01-01", periods=28)
rows = []
for s in (1, 2, 3):
    for f in ("DAIRY", "BOOKS"):
        base = {"DAIRY": 100, "BOOKS": 3}[f] * s
        weekly = 1 + 0.3 * np.sin(2 * np.pi * days.dayofweek / 7)
        sales = np.round(base * weekly * rng.lognormal(0, 0.1, len(days)), 1)
        rows.append(pd.DataFrame({"store_nbr": s, "family": f, "date": days, "sales": sales}))
df = pd.concat(rows, ignore_index=True)

H = 7
valid_start = df["date"].max() - pd.Timedelta(days=H - 1)
fit, valid = df[df["date"] < valid_start], df[df["date"] >= valid_start].copy()

def rmsle(y_true, y_pred):
    y_pred = np.clip(y_pred, 0, None)
    return float(np.sqrt(np.mean((np.log1p(y_pred) - np.log1p(y_true)) ** 2)))

last = fit["date"].max()
valid["src_date"] = valid["date"] - pd.to_timedelta(np.ceil((valid["date"] - last).dt.days / 7).astype(int) * 7, unit="D")
src = fit.rename(columns={"date": "src_date", "sales": "pred"})
valid = valid.merge(src, on=["store_nbr", "family", "src_date"], how="left")

print("rows scored:", len(valid))
print("RMSLE seasonal naive:", round(rmsle(valid["sales"].values, valid["pred"].values), 4))
print("RMSLE all zeros:     ", round(rmsle(valid["sales"].values, np.zeros(len(valid))), 4))
# Output:
# rows scored: 42
# RMSLE seasonal naive: 0.1385
# RMSLE all zeros:      3.9387
```

Seasonal naive is far better than zeros. The remaining error comes from random noise, which no weekly rule can remove.

## Common mistakes

- Using a random split, or validation days from the middle of the history.
- Forgetting that `test` has no `sales`, and building lag features that need them (we fix this in part 2).
- Using `np.log` instead of `np.log1p`.
- Predicting negative sales.
- Dropping the missing calendar days and then using `shift` by rows, which shifts by the wrong number of days.
- Ignoring zero-sales stores at the start of the history.
- Not submitting a baseline first.

## Interview lens

**Typical question:** "You join a forecasting project with thousands of store-product series. What do you do in the first two days?"

**Strong answer:** "I read the decision and the metric first. Here the metric is RMSLE, a relative error, so I work on a log scale. I explore dates, missing days, zero share and the series count. I build a validation that copies the test: the last 16 days, trained on the past only. Then I build three baselines: zeros, a recent mean and seasonal naive, and I record their scores. Only after that I add features and a global model such as LightGBM. I report the lift over seasonal naive."

**Red flags:** starting with a deep network; a random split; no baseline numbers; ignoring zeros and missing days.

## Real world

- Store Sales uses data from Corporación Favorita, a large grocery retailer in Ecuador. It is a long-running "Getting Started" competition on Kaggle. The public notebooks and course material around it are a common first step into forecasting.
- A related, earlier competition on Kaggle used the same retailer's data. It was Corporación Favorita Grocery Sales Forecasting (2017-2018), with a much larger number of items.

## Key points

- Task: forecast sales for 54 stores x 33 families for 16 days; metric RMSLE (relative error, lower is better).
- Explore: dates, missing days, zero share, series count, weekly pattern.
- Validation: last 16 days of train as validation, fit on the past only.
- Baselines: zeros, recent mean, seasonal naive. Submit the seasonal naive first.
- Train on `log1p(sales)` with squared error and you optimise RMSLE directly.
