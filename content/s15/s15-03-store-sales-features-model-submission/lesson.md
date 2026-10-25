---
id: s15-03-store-sales-features-model-submission
title: Store Sales, part 2 - features, LightGBM, error analysis and submission
minutes: 60
level: intermediate
goals: [Build lag, rolling, calendar, holiday, oil and promotion features without leakage, Train one global LightGBM on log1p sales, Do error analysis by family, store and day, Create the final submission and list the next ideas]
prereqs: [s15-02-store-sales-baseline-validation]
tags: [kaggle, store-sales, lightgbm, features, error-analysis, submission]
skills: [leakage, scale, baseline-first]
---

## Warm-up

```check
{"q": "From part 1: the test period is 16 days. How should the validation set be built?", "type": "single",
 "options": ["16 random days", "The last 16 days of train, fitting only on the days before", "The first 16 days", "All days"],
 "answer": 1,
 "why": ["Random days leak neighbours.", "Correct.", "Not like the test.", "No honest score."]}
```

## Why it matters

Part 1 gave you a baseline. Now you build the model that wins the points. The plan is the same one top competitors use for many sales problems: **one global gradient boosting model** trained on all series, with careful features. The hard part is not LightGBM. The hard part is making features that are **available at forecast time**. A single wrong lag can make your validation look great and your submission bad.

## Step 6: the one rule for features

When you forecast the 16 days after the last known day `T`, you do **not** know the sales of those days. For the 16th day you also do not know the 15 days before it. So:

> A feature for date `d` may only use sales from dates **at least 16 days before `d`**.

That means lag 16 or more. We use lags 16, 21, 28, 35, 42 and 364. Lags 21, 28, 35 and 42 are whole weeks, so they keep the weekday. We call this a **direct** strategy with long lags: one model predicts all 16 days with the same features. (A recursive model with lag 1 is possible, but errors pile up and the code is longer.)

Rolling means follow the same rule: shift by 16 first, then take the window.

Features that are **known in the future** can use the date itself: day of week, day of month, month, payday, holidays, `onpromotion`, and store details.

```chart
{"title": "Which sales can a feature use? (forecast origin at day 0, horizon 16)", "x": "days before target date", "height": 200,
 "series": [
   {"name": "usable (1 = yes)", "kind": "bar", "x": [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21], "y": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1]}
 ],
 "caption": "For the last day of the test period, only sales 16 or more days back exist. Using lag 1 to 15 would need sales that you do not have."}
```

```check
{"q": "You forecast 16 days ahead. Which feature is safe for every day of the test period?", "type": "single",
 "options": ["lag_1 (sales of the day before)", "lag_7 (sales one week before)", "lag_21 (sales three weeks before)", "mean of sales over the next 7 days"],
 "answer": 2,
 "why": ["For day 5 of the test period, lag 1 is a test day: unknown.", "For day 10, lag 7 falls inside the test period: unknown.", "Correct: 21 is more than 16, so the value is always in the known history.", "That is the future."]}
```

## Step 7: build the feature table

First make a complete grid: every series on every calendar day, including the missing days and the test days. This makes `shift(k)` mean "k days" and not "k rows". Then add features.

```notebook
# Continue in the same notebook as part 1 (train, test, stores, oil, holidays are loaded)
import lightgbm as lgb

H = 16
TRAIN_FROM = "2016-01-01"                  # use the last years only: faster, and closer to the test period

dates = pd.date_range(train["date"].min(), test["date"].max(), freq="D")
series = train[["store_nbr", "family"]].drop_duplicates()
grid = series.merge(pd.DataFrame({"date": dates}), how="cross")        # every series x every day
raw = pd.concat([train, test], ignore_index=True)                      # test rows have no sales
full = grid.merge(raw, on=["store_nbr", "family", "date"], how="left")
full = full.sort_values(["store_nbr", "family", "date"]).reset_index(drop=True)
full["onpromotion"] = full["onpromotion"].fillna(0)
full["y"] = np.log1p(full["sales"])                                    # NaN for test days and missing days

# Series are "active" from their first non-zero sale. Earlier zeros are mostly "store not open yet".
first_sale = train[train["sales"] > 0].groupby(["store_nbr", "family"])["date"].min().rename("first_sale").reset_index()
full = full.merge(first_sale, on=["store_nbr", "family"], how="left")
full["active"] = full["date"] >= full["first_sale"]                    # False when first_sale is missing

# Lag and rolling features. Every one of them ends at least H days before the target date.
g = full.groupby(["store_nbr", "family"])["y"]
lags = [16, 21, 28, 35, 42, 364]
for k in lags:
    full[f"lag_{k}"] = g.shift(k)
for w in [7, 14, 28, 91]:
    full[f"mean_{w}"] = g.transform(lambda s, w=w: s.shift(H).rolling(w, min_periods=1).mean())

# Promotions are known for the test days, so a window that includes today is allowed
full["promo_mean_7"] = full.groupby(["store_nbr", "family"])["onpromotion"].transform(lambda s: s.rolling(7, min_periods=1).mean())

# Calendar features
full["dow"] = full["date"].dt.dayofweek
full["dom"] = full["date"].dt.day
full["month"] = full["date"].dt.month
full["payday"] = ((full["dom"] == 15) | full["date"].dt.is_month_end).astype(int)

# National holidays. Rows with transferred == True are NOT celebrated on that date.
nat = holidays[(holidays["locale"] == "National") & (~holidays["transferred"])
               & holidays["type"].isin(["Holiday", "Transfer", "Additional", "Bridge"])]
full["holiday"] = full["date"].isin(nat["date"]).astype(int)

# Oil price: one value per calendar day (forward fill, then backward fill)
oil_daily = oil.set_index("date")["dcoilwtico"].reindex(dates).ffill().bfill()
full["oil"] = full["date"].map(oil_daily)

# Store details and categories
full = full.merge(stores.rename(columns={"type": "store_type"}), on="store_nbr", how="left")
full["store"] = full["store_nbr"].astype("category")
for c in ["family", "city", "state", "store_type"]:
    full[c] = full[c].astype("category")

features = (["store", "family", "city", "state", "store_type", "cluster", "onpromotion", "promo_mean_7",
             "dow", "dom", "month", "payday", "holiday", "oil"]
            + [f"lag_{k}" for k in lags] + [f"mean_{w}" for w in [7, 14, 28, 91]])
print(len(features), "features;", full.shape[0], "rows in the grid")
```

The mini problem [[problem:daily-oil-fill]] is the oil step in small. Notes on the choices:

- `transactions.csv` is **not** used: it has no rows for the test period, so it would need lags of 16 days or more. You can try that later.
- Only **national** holidays are used. Local and regional holidays apply to some cities only. Adding them is a good next step.
- `first_sale` removes the long zero runs before a series started. The model does not learn "zero" from stores that were not open.

```check
{"q": "Why is `g.transform(lambda s: s.shift(H).rolling(w).mean())` safe, while `s.rolling(w).mean()` would not be?", "type": "single",
 "options": ["shift makes it faster", "shift(H) moves the window so it ends H days before the target date", "rolling needs shift to run", "No difference"],
 "answer": 1,
 "why": ["Speed is not the point.", "Correct: the window then uses only sales older than the forecast horizon.", "rolling runs without shift.", "Without shift the window includes the day itself and recent days that are unknown at forecast time."]}
```

## Step 8: train and validate

Use the same validation as in part 1: fit on days before `valid_start`, test on the last 16 days. The model predicts `y = log1p(sales)`, so its RMSE on `y` is the RMSLE.

```notebook
train_rows = full["sales"].notna() & full["active"] & (full["date"] >= TRAIN_FROM)
fit_idx = train_rows & (full["date"] < valid_start)
val_idx = train_rows & (full["date"] >= valid_start)

params = dict(n_estimators=2000, learning_rate=0.05, num_leaves=63, min_child_samples=50,
              subsample=0.8, subsample_freq=1, colsample_bytree=0.8, reg_lambda=1.0,
              n_jobs=-1, random_state=42, verbose=-1)
model = lgb.LGBMRegressor(**params)
model.fit(full.loc[fit_idx, features], full.loc[fit_idx, "y"],
          eval_set=[(full.loc[val_idx, features], full.loc[val_idx, "y"])], eval_metric="rmse",
          callbacks=[lgb.early_stopping(100, verbose=False), lgb.log_evaluation(0)])
best_iter = model.best_iteration_
print("best number of trees:", best_iter)

# Predictions for ALL validation rows (inactive series get 0)
vp = full[(full["date"] >= valid_start) & full["sales"].notna()].copy()
vp["pred_log"] = 0.0
act = vp["active"]
vp.loc[act, "pred_log"] = np.clip(model.predict(vp.loc[act, features]), 0, None)

# Series with no sales in the last 14 days of the fit period: predict 0
recent = fit[fit["date"] >= fit["date"].max() - pd.Timedelta(days=13)].groupby(["store_nbr", "family"])["sales"].sum()
dead = recent[recent == 0].index
vp["dead"] = pd.MultiIndex.from_frame(vp[["store_nbr", "family"]]).isin(dead)
vp.loc[vp["dead"], "pred_log"] = 0.0

print("RMSLE LightGBM:", round(float(np.sqrt(np.mean((vp["pred_log"] - vp["y"]) ** 2))), 4))
```

Compare with the baselines from part 1. A good result is a clear drop from the seasonal naive score. Early stopping used the validation days to choose the number of trees, so the score is a little optimistic. For a stricter test, add a second validation window.

```check
{"q": "Why can the validation score be slightly optimistic when you use early stopping on the same validation set?", "type": "single",
 "options": ["Early stopping uses the test labels", "The number of trees was chosen using the validation labels", "LightGBM always overfits", "RMSLE is biased"],
 "answer": 1,
 "why": ["It uses validation labels, not the hidden test labels.", "Correct: a small selection effect. Use a second window to check.", "Not always.", "RMSLE is not biased in this way."]}
```

## Step 9: error analysis

A single score hides where the model fails. Break the error down by family, store, day and feature importance.

```notebook
vp["se"] = (vp["pred_log"] - vp["y"]) ** 2
print("--- worst families (RMSLE)")
print(vp.groupby("family", observed=True)["se"].mean().pow(0.5).sort_values(ascending=False).head(8).round(3))
print("--- worst stores")
print(vp.groupby("store_nbr")["se"].mean().pow(0.5).sort_values(ascending=False).head(5).round(3))
print("--- error by day of the validation period")
print(vp.groupby("date")["se"].mean().pow(0.5).round(3).to_string())
print("--- top features")
print(pd.Series(model.feature_importances_, index=features).sort_values(ascending=False).head(10))
```

What to look for (check on the real data):

- **Rare families** (many zeros, small counts) usually have the highest error. Their sales are noisy and RMSLE is relative.
- **Days near holidays and paydays** may have larger errors.
- **Error by horizon:** the last test days are harder, because the lags are older.
- If one store or family is far worse, look at its plot and its start date.

Write one idea per finding. For example: "Family X is noisy: try a smoother model for rare families." Then test one idea at a time on the validation set.

## Step 10: final model and submission

Now train on **all** known days and predict the test period. Use a few more trees than the best validation round, because there is more data.

```notebook
final_params = {**params, "n_estimators": int(best_iter * 1.1)}
final = lgb.LGBMRegressor(**final_params)
final.fit(full.loc[train_rows, features], full.loc[train_rows, "y"])

tp = full[full["date"] > last_day].copy()                         # the 16 test days
tp["pred_log"] = 0.0
act = tp["active"]
tp.loc[act, "pred_log"] = np.clip(final.predict(tp.loc[act, features]), 0, None)

recent_all = train[train["date"] >= last_day - pd.Timedelta(days=13)].groupby(["store_nbr", "family"])["sales"].sum()
dead_all = recent_all[recent_all == 0].index
tp.loc[pd.MultiIndex.from_frame(tp[["store_nbr", "family"]]).isin(dead_all), "pred_log"] = 0.0
tp["sales"] = np.expm1(tp["pred_log"])                            # back from the log scale

sub = test[["id", "store_nbr", "family", "date"]].merge(
    tp[["store_nbr", "family", "date", "sales"]], on=["store_nbr", "family", "date"], how="left")
assert sub["sales"].notna().all() and len(sub) == len(test)
sub[["id", "sales"]].to_csv("submission.csv", index=False)
print(sub[["id", "sales"]].head())
```

Save a version, submit, and write down: validation score, public score, and what you changed. If the public score is much worse than validation, look for leakage first.

## Ideas for the next version

1. Add a second and third validation window (for example ending 16 and 32 days earlier).
2. Add local and regional holidays by matching `city` and `state`, and the earthquake period in April 2016.
3. Add features from `transactions.csv` with lag of 16 days or more.
4. Train separate models for groups of families, or add family-level sales means as features.
5. Average several seeds, or blend with a model such as Ridge or a neural network.
6. Try a recursive model with short lags for the first days only.

## Worked example

A small version in the browser: four stores, 120 days, a 16-day test. We build lag and rolling features with the 16-day rule, check the timing, and fit a linear model with numpy. We compare it with seasonal naive on the last 16 days.

```python
import numpy as np
import pandas as pd

rng = np.random.default_rng(1)
days = pd.date_range("2024-01-01", periods=120)
rows = []
for s in (1, 2, 3, 4):
    base = 40 * s
    weekly = 1 + 0.3 * np.sin(2 * np.pi * days.dayofweek / 7)
    sales = np.round(base * weekly * (1 + 0.003 * np.arange(len(days))) * rng.lognormal(0, 0.1, len(days)), 1)
    rows.append(pd.DataFrame({"store_nbr": s, "date": days, "sales": sales}))
df = pd.concat(rows, ignore_index=True).sort_values(["store_nbr", "date"]).reset_index(drop=True)

H = 16
df["y"] = np.log1p(df["sales"])
g = df.groupby("store_nbr")["y"]
df["lag_21"] = g.shift(21)                                          # same weekday, 3 weeks back
df["lag_28"] = g.shift(28)
df["mean_14"] = g.transform(lambda s: s.shift(H).rolling(14, min_periods=1).mean())   # window ends 16 days back
df["dow"] = df["date"].dt.dayofweek

last_known = days[-H - 1]                                           # pretend sales end here
test_days = days[-H:]
first, last = test_days[0], test_days[-1]
print("last known day:", last_known.date())
print("newest day used by mean_14 for", first.date(), "->", (first - pd.Timedelta(days=H)).date())
print("newest day used by mean_14 for", last.date(), "->", (last - pd.Timedelta(days=H)).date())
print("all inside the known period:", (last - pd.Timedelta(days=H)) <= last_known)

feat = ["lag_21", "lag_28", "mean_14"]
fit = df[(df["date"] <= last_known) & df[feat].notna().all(axis=1)]
test = df[df["date"] > last_known].copy()
X = np.column_stack([np.ones(len(fit))] + [fit[c] for c in feat])
coef, *_ = np.linalg.lstsq(X, fit["y"].to_numpy(), rcond=None)
Xt = np.column_stack([np.ones(len(test))] + [test[c] for c in feat])
test["pred"] = np.clip(Xt @ coef, 0, None)

# seasonal naive: same weekday of the last known week
src = test["date"] - pd.to_timedelta(np.ceil((test["date"] - last_known).dt.days / 7).astype(int) * 7, unit="D")
sn = df.set_index(["store_nbr", "date"])["y"].reindex(pd.MultiIndex.from_arrays([test["store_nbr"], src])).to_numpy()

rmse = lambda a, b: float(np.sqrt(np.mean((a - b) ** 2)))
print("RMSLE seasonal naive:", round(rmse(sn, test["y"].to_numpy()), 4))
print("RMSLE linear on lag features:", round(rmse(test["pred"].to_numpy(), test["y"].to_numpy()), 4))
# Output:
# last known day: 2024-04-13
# newest day used by mean_14 for 2024-04-14 -> 2024-03-29
# newest day used by mean_14 for 2024-04-29 -> 2024-04-13
# all inside the known period: True
# RMSLE seasonal naive: 0.1347
# RMSLE linear on lag features: 0.1122
```

The check lines show that the newest sales used by the rolling mean for the last test day are from the last known day, never later. A tiny linear model on three lag features already beats seasonal naive here, because it averages out noise. A LightGBM model on the real data adds many more features and non-linear effects.

## Common mistakes

- Features with lags shorter than the horizon (for example lag 1 or 7 for a 16-day task).
- Rolling windows without `shift`.
- Shifting by rows after dropping missing days.
- Training on the zero rows before a store opened.
- Using `transactions` of the test days (not available).
- Predicting `sales` directly with squared error: the model then optimises the wrong metric.
- Forgetting to convert predictions back with `np.expm1`.
- Fitting the final model with the same number of trees and no check of the public score.

## Interview lens

**Typical question:** "How would you build a model for 1,800 store-product series with a 16-day horizon?"

**Strong answer:** "I build one global LightGBM model on log1p of sales, because the metric is RMSLE and sharing patterns across series helps the rare ones. I make a complete date grid so that lags mean days. All lag and rolling features end at least 16 days before the target, so the same model works for every day of the horizon. I add calendar, holiday, promotion, oil and store features, and I remove the zero period before a store opened. I validate on the last 16 days and compare with seasonal naive. I analyse errors by family, store and day, and I add a second validation window before I trust small gains."

**Red flags:** random split; lag 1 features for a 16-day horizon; no baseline; training on raw sales with an RMSE loss.

## Real world

- Store Sales is a popular course project, and many public notebooks use gradient boosting with lag and calendar features, as well as simple linear models with seasonal features. Compare several of them and look at how they validate.
- In the related M5 competition (see the next lesson) gradient boosting on lag features was the winning style, which is why we use it here.

## Key points

- A feature for date `d` may use sales only from dates at least 16 days before `d`: lags 16 or more, and rolling windows after `shift(16)`.
- Build a complete date grid first, so that `shift(k)` means `k` days.
- Train one global LightGBM on `log1p(sales)`; its RMSE is the RMSLE.
- Remove the zero period before a series started; predict 0 for series that are dead.
- Analyse errors by family, store and day; improve one thing at a time on validation.
