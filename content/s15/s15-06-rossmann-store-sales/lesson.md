---
id: s15-06-rossmann-store-sales
title: Rossmann Store Sales - promotions, holidays and entity embeddings
minutes: 50
level: intermediate
goals: [Explain the Rossmann task and the RMSPE metric, Build calendar, promotion and competition features, Train a LightGBM model on log sales and score RMSPE, Describe how entity embeddings turn categories into numbers for a neural network]
prereqs: [s15-03-store-sales-features-model-submission]
tags: [kaggle, rossmann, RMSPE, promotions, holidays, entity-embeddings]
skills: [metrics, baseline-first, leakage]
---

## Warm-up

```check
{"q": "A percentage error is undefined for which actual value?", "type": "single",
 "options": ["1", "0", "100", "-1"],
 "answer": 1,
 "why": ["Defined.", "Correct: division by zero.", "Defined.", "Defined, but sales are not negative."]}
```

```check
{"q": "A feature is known for the test period only if it is:", "type": "single",
 "options": ["Sales of the same day", "A calendar or planned value, such as a promotion flag", "Customers of the same day", "The target"],
 "answer": 1,
 "why": ["Unknown.", "Correct: planned inputs are in the test file.", "Customers are not in the test file.", "Unknown."]}
```

## Why it matters

*Rossmann Store Sales* (2015) asked competitors to forecast daily sales for **1,115 Rossmann drug stores in Germany** for six weeks. It is a classic because the lessons are clear. Promotions and holidays drive sales. Stores differ a lot. You can win with good features and gradient boosting. It is also famous for the **entity embeddings** paper from the 3rd-place team. Interviewers like it as a case for tabular time series.

## Goal and metric

**Task.** Predict `Sales` for each store and day in the test period. The test period is August 1 to September 17, 2015 (48 days). The training data run from January 2013 to July 2015.

**Metric: RMSPE**

`RMSPE = sqrt( mean( ((y − p) / y)² ) )`

- It is a **relative** error. A store with small sales counts as much as a big store.
- Days with `y = 0` are **ignored** in scoring (the store is closed).
- Over-forecasts and under-forecasts are punished differently. If y = 100, then p = 150 gives 0.5 and p = 50 also gives 0.5. But p = 0 gives 1. A model that predicts too low cannot get more than 1 per row; too high can be larger.

Practise it in [[problem:rmspe-open-rule]].

```check
{"q": "Actual sales are 200 and the prediction is 250. What is the percentage error term (not squared)?", "type": "numeric",
 "answer": 0.25, "tol": 0.001, "why": "(200 − 250) / 200 = −0.25. Squared it is 0.0625; the sign does not matter after squaring."}
```

## Files

| File | Columns |
|---|---|
| `train.csv` | `Store, DayOfWeek, Date, Sales, Customers, Open, Promo, StateHoliday, SchoolHoliday` |
| `test.csv` | `Id, Store, DayOfWeek, Date, Open, Promo, StateHoliday, SchoolHoliday` |
| `store.csv` | `Store, StoreType, Assortment, CompetitionDistance, CompetitionOpenSinceMonth, CompetitionOpenSinceYear, Promo2, Promo2SinceWeek, Promo2SinceYear, PromoInterval` |
| `sample_submission.csv` | `Id, Sales` |

`Customers` is **not** in the test file, so you cannot use it. `Promo` is a daily promotion flag. `Promo2` is a second, continuing promotion that runs in some stores in certain months (`PromoInterval`, for example `Jan,Apr,Jul,Oct`). `StateHoliday` holds `0`, `a`, `b` or `c` as text. A few test rows may have a missing `Open`: check the Data tab.

## Data tour

```notebook
# Run this in a Kaggle notebook (Data: Rossmann Store Sales)
import numpy as np
import pandas as pd
import lightgbm as lgb

DATA = "/kaggle/input/rossmann-store-sales/"
train = pd.read_csv(DATA + "train.csv", parse_dates=["Date"], dtype={"StateHoliday": str})
test = pd.read_csv(DATA + "test.csv", parse_dates=["Date"], dtype={"StateHoliday": str})
store = pd.read_csv(DATA + "store.csv")

print(train["Date"].min().date(), "to", train["Date"].max().date(), "| stores:", train["Store"].nunique())
print("test:", test["Date"].min().date(), "to", test["Date"].max().date(), "| rows:", len(test))
print("closed days:", round(float((train["Open"] == 0).mean()), 3),
      "| sales on closed days:", float(train.loc[train["Open"] == 0, "Sales"].sum()))
print("missing Open in test:", int(test["Open"].isna().sum()))

open_days = train[(train["Open"] == 1) & (train["Sales"] > 0)]
print(open_days.groupby("Promo")["Sales"].mean().round(0))                 # promotion effect
print(open_days.groupby("DayOfWeek")["Sales"].mean().round(0))             # weekday pattern
print(open_days.groupby(open_days["Date"].dt.month)["Sales"].mean().round(0).head(12))
```

Things you should find on the real data: sales on closed days are zero. `Promo` raises average sales a lot. There is a weekday pattern and a December peak. Look for yourself.

## Baseline and validation

- **Validation:** the last 48 days of the training data (same length as the test).
- **Baseline:** the median sales per (store, weekday, promo) from the fit part, over open days. Predict 0 when the store is closed.

```notebook
H = 48
valid_start = train["Date"].max() - pd.Timedelta(days=H - 1)
fit, valid = train[train["Date"] < valid_start], train[train["Date"] >= valid_start].copy()

def rmspe(y_true, y_pred):
    y_true, y_pred = np.asarray(y_true, float), np.asarray(y_pred, float)
    m = y_true != 0
    return float(np.sqrt(np.mean(((y_true[m] - y_pred[m]) / y_true[m]) ** 2)))

fit_open = fit[(fit["Open"] == 1) & (fit["Sales"] > 0)]
base = (fit_open.groupby(["Store", "DayOfWeek", "Promo"])["Sales"].median().rename("pred").reset_index())
v = valid.merge(base, on=["Store", "DayOfWeek", "Promo"], how="left")
v["pred"] = v["pred"].fillna(fit_open["Sales"].median()).where(v["Open"] != 0, 0.0)
print("RMSPE baseline (store x weekday x promo median):", round(rmspe(v["Sales"], v["pred"]), 4))
```

```chart
{"title": "Promotion lifts sales: a store with a promotion every second week", "x": "day", "height": 220,
 "series": [
   {"name": "sales", "gen": [["const", {"value": 100}], ["season", {"period": 14, "amp": 25}], ["noise", {"sd": 4}]], "n": 70, "seed": 9}
 ],
 "caption": "The promotion pattern repeats. A model must know the promotion flag for the future day, and the test file has it."}
```

## Features

The test file gives dates, `Promo`, holidays and `Open`. So you can use all calendar and promotion information, plus store information. Sales lags are not needed for a 48-day horizon. Instead use **store-level statistics from the fit part only**, to avoid leakage.

- **Calendar:** day of week, day, month, week of year, year, days to the end of the month.
- **Promotions:** `Promo`, `SchoolHoliday`, `StateHoliday` (as category), `Promo2` active in the month.
- **Competition:** how many months the nearest competitor has been open, and the distance.
- **Store statistics:** mean log sales per store, per store and weekday, per store and promo, computed on the fit part.

```notebook
MONTHS = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun", 7: "Jul", 8: "Aug", 9: "Sept", 10: "Oct", 11: "Nov", 12: "Dec"}

def add_features(df, store, stats_source):
    df = df.merge(store, on="Store", how="left")
    d = df["Date"]
    df["day"], df["month"], df["year"] = d.dt.day, d.dt.month, d.dt.year
    df["weekofyear"] = d.dt.isocalendar().week.astype(int)
    df["days_to_month_end"] = d.dt.days_in_month - d.dt.day
    # months since the competitor opened (0 if not open yet, NaN if unknown)
    comp = 12 * (df["year"] - df["CompetitionOpenSinceYear"]) + (df["month"] - df["CompetitionOpenSinceMonth"])
    df["competition_months"] = comp.clip(lower=0)
    # Promo2 is active if it has started and the month is in the interval
    start = (pd.to_datetime(df["Promo2SinceYear"].fillna(2100).astype(int).astype(str) + "-01-01")
             + pd.to_timedelta((df["Promo2SinceWeek"].fillna(1) - 1) * 7, unit="D"))
    in_month = [(m in str(i).split(",")) for m, i in zip(d.dt.month.map(MONTHS), df["PromoInterval"])]
    df["promo2_active"] = ((df["Promo2"] == 1) & (d >= start) & np.array(in_month)).astype(int)
    # Store statistics from the fit data only
    s = stats_source[(stats_source["Open"] == 1) & (stats_source["Sales"] > 0)].copy()
    s["ls"] = np.log1p(s["Sales"])
    df = df.merge(s.groupby("Store")["ls"].mean().rename("store_mean").reset_index(), on="Store", how="left")
    df = df.merge(s.groupby(["Store", "DayOfWeek"])["ls"].mean().rename("store_dow_mean").reset_index(), on=["Store", "DayOfWeek"], how="left")
    df = df.merge(s.groupby(["Store", "Promo"])["ls"].mean().rename("store_promo_mean").reset_index(), on=["Store", "Promo"], how="left")
    for c in ["StateHoliday", "StoreType", "Assortment", "PromoInterval"]:
        df[c] = df[c].fillna("none").astype("category")
    df["Store"] = df["Store"].astype("category")
    return df

features = ["Store", "DayOfWeek", "Promo", "StateHoliday", "SchoolHoliday", "StoreType", "Assortment",
            "CompetitionDistance", "competition_months", "Promo2", "promo2_active", "day", "month", "year",
            "weekofyear", "days_to_month_end", "store_mean", "store_dow_mean", "store_promo_mean"]
```

```check
{"q": "Why compute store_mean from the fit part only when validating?", "type": "single",
 "options": ["It is faster", "Using validation days would put the answer into the feature (leakage)", "Means are not allowed in LightGBM", "To get more rows"],
 "answer": 1,
 "why": ["Not the reason.", "Correct: statistics must come from the past of the rows you predict.", "They are allowed.", "No."]}
```

## Model and validation

Train on **open days with positive sales**. Use `log1p(Sales)` as the target. RMSE on the log scale is close to the relative error that RMSPE measures. Then predict, convert with `expm1`, and set closed days to 0.

```notebook
def fit_model(train_df, features, n_estimators, valid_df=None):
    params = dict(n_estimators=n_estimators, learning_rate=0.05, num_leaves=63, min_child_samples=30,
                  subsample=0.8, subsample_freq=1, colsample_bytree=0.8, n_jobs=-1, random_state=42, verbose=-1)
    m = lgb.LGBMRegressor(**params)
    X, y = train_df[features], np.log1p(train_df["Sales"])
    if valid_df is None:
        return m.fit(X, y)
    return m.fit(X, y, eval_set=[(valid_df[features], np.log1p(valid_df["Sales"]))], eval_metric="rmse",
                 callbacks=[lgb.early_stopping(100, verbose=False), lgb.log_evaluation(0)])

tr = add_features(fit[(fit["Open"] == 1) & (fit["Sales"] > 0)], store, fit)
va_all = add_features(valid, store, fit)
va_open = va_all[(va_all["Open"] == 1) & (va_all["Sales"] > 0)]
model = fit_model(tr, features, 3000, va_open)

va_all["pred"] = np.expm1(model.predict(va_all[features]))
va_all.loc[va_all["Open"] == 0, "pred"] = 0.0
print("best number of trees:", model.best_iteration_)
print("RMSPE LightGBM:", round(rmspe(va_all["Sales"], va_all["pred"]), 4))
```

Compare with the baseline score. Many public solutions also multiplied predictions by a number a little below 1 (about 0.98 to 0.99). RMSPE punishes high predictions harder than low ones. Test such a factor on your validation set; do not copy it blindly.

## Error analysis and submission

```notebook
va_open = va_all[va_all["Sales"] > 0].copy()
va_open["pe2"] = ((va_open["Sales"] - va_open["pred"]) / va_open["Sales"]) ** 2
print("--- worst stores")
print(va_open.groupby(va_open["Store"].astype(int))["pe2"].mean().pow(0.5).sort_values(ascending=False).head(5).round(3))
print("--- by promo")
print(va_open.groupby("Promo")["pe2"].mean().pow(0.5).round(3))
print("--- by state holiday")
print(va_open.groupby("StateHoliday", observed=True)["pe2"].mean().pow(0.5).round(3))

# Final model on all known days, then the submission
all_tr = add_features(train[(train["Open"] == 1) & (train["Sales"] > 0)], store, train)
final = fit_model(all_tr, features, int(model.best_iteration_ * 1.1))
te = add_features(test, store, train)
te["Sales"] = np.expm1(final.predict(te[features]))
te.loc[te["Open"] == 0, "Sales"] = 0.0                       # NaN Open is treated as open
te[["Id", "Sales"]].sort_values("Id").to_csv("submission.csv", index=False)
print(te[["Id", "Sales"]].head())
```

Look at the worst stores, the promotion effect and holiday days. Typical improvements: more careful holiday features (days before and after), competition effects, store-level clusters, and averaging several models.

## Entity embeddings: the 3rd-place idea

Trees handle categories like `Store` or `DayOfWeek` by splitting. A neural network needs numbers. One-hot encoding of 1,115 stores is large and treats all stores as unrelated. In 2016 the 3rd-place team (Cheng Guo and Felix Berkhahn) described **entity embeddings**. Each category value gets a short learned vector, for example 10 numbers for a store. The network learns the vectors during training, so similar stores get similar vectors. They fed the embeddings and the other features to a small fully connected network. They reported good results with little feature engineering. The paper is *Entity Embeddings of Categorical Variables* (2016).

```notebook
# Sketch of the idea (not run in this lesson): a store embedding table of size 1115 x 10
# store_vec = embedding_table[store_index]      # a learned vector, shape (10,)
# x = concat([store_vec, weekday_vec, numeric_features])
# prediction = small_mlp(x)                      # trained on log sales
```

## Worked example

A small version in the browser: three stores with a weekly pattern and a promotion. We compute the baseline median per (store, weekday, promo) and score it with RMSPE, ignoring closed days.

```python
import numpy as np
import pandas as pd

rng = np.random.default_rng(3)
days = pd.date_range("2024-01-01", periods=84)
rows = []
for s, base in [(1, 3000), (2, 5000), (3, 8000)]:
    promo = ((np.arange(84) // 7) % 2 == 0).astype(int)                 # promotion every second week
    sales = base * (1 + 0.25 * promo) * rng.lognormal(0, 0.08, 84)
    open_ = (days.dayofweek != 6).astype(int)                           # closed on Sundays
    rows.append(pd.DataFrame({"Store": s, "Date": days, "DayOfWeek": days.dayofweek + 1, "Promo": promo,
                              "Open": open_, "Sales": (sales * open_).round()}))
df = pd.concat(rows, ignore_index=True)

split = days[-14]
fit, valid = df[df["Date"] < split], df[df["Date"] >= split].copy()

def rmspe(y, p):
    y, p = np.asarray(y, float), np.asarray(p, float)
    m = y != 0                                                          # closed days are not scored
    return float(np.sqrt(np.mean(((y[m] - p[m]) / y[m]) ** 2)))

fo = fit[(fit["Open"] == 1) & (fit["Sales"] > 0)]
med = fo.groupby(["Store", "DayOfWeek", "Promo"])["Sales"].median().rename("pred").reset_index()
store_mean = fo.groupby("Store")["Sales"].mean().rename("smean").reset_index()
v = valid.merge(med, on=["Store", "DayOfWeek", "Promo"], how="left").merge(store_mean, on="Store")
v["pred"] = v["pred"].fillna(v["smean"]).where(v["Open"] != 0, 0.0)
v["smean"] = v["smean"].where(v["Open"] != 0, 0.0)

print("scored rows:", int((v["Sales"] != 0).sum()), "of", len(v))
print("RMSPE store mean       :", round(rmspe(v["Sales"], v["smean"]), 4))
print("RMSPE store x dow x promo median:", round(rmspe(v["Sales"], v["pred"]), 4))
# Output:
# scored rows: 36 of 42
# RMSPE store mean       : 0.1279
# RMSPE store x dow x promo median: 0.0761
```

Knowing the promotion flag removes a big part of the error. Closed Sundays are ignored by the metric, and predicting 0 for them is still correct.

## Common mistakes

- Dividing by the prediction instead of the actual.
- Including closed days (`Sales = 0`) in the metric or in the training set.
- Using `Customers` as a feature: it is not in the test file.
- Store statistics computed on the validation days (leakage).
- Reading `StateHoliday` with mixed types (numbers and text) without `dtype=str`.
- Forgetting the missing `Open` values in the test file.
- Random split of days.

## Interview lens

**Typical question:** "How do you handle a metric like RMSPE in a forecasting model?"

**Strong answer:** "RMSPE is a relative error, so I train on log sales. Squared error on the log scale is close to squared relative error. I train only on open days with positive sales. I ignore closed days in validation, as the metric does. I predict zero when the store is closed. Because the metric punishes over-forecasts more than under-forecasts, I test a small down-scaling factor on validation. I use calendar, promotion and competition features and store-level statistics computed only on past data."

**Red flags:** training on closed days; MAE loss with no thought about the metric; leakage from validation days.

## Real world

- Rossmann Store Sales ran on Kaggle in 2015. Top solutions used gradient boosted trees with many calendar and promotion features. The 3rd-place team used neural networks with entity embeddings and published the method.
- The entity embeddings idea is now common in tabular deep learning. It is used for ids such as store, item or user in recommendation and forecasting models.

## Key points

- Task: daily sales for 1,115 stores, 48-day horizon; metric RMSPE ignoring zero-sales days.
- Features known in the test file: calendar, Promo, holidays, Open; add store attributes and past-only store statistics.
- Train on open days with log1p(Sales); predict 0 for closed stores.
- Check the error by store, promotion and holiday.
- Entity embeddings give each category a learned vector for neural networks.
