---
id: s15-05-predict-future-sales
title: Predict Future Sales (1C Company) - monthly data and lag features
minutes: 50
level: intermediate
goals: [Aggregate daily sale lines to monthly counts per shop and item, Clip the target to 0-20 like the metric, Build lag and mean-encoding features without leakage, Handle new shop-item pairs in the test month]
prereqs: [s15-03-store-sales-features-model-submission]
tags: [kaggle, predict-future-sales, 1C, lag-features, monthly, clipping]
skills: [leakage, pandas-fluency, baseline-first]
---

## Warm-up

```check
{"q": "Why is `shift(1)` on a table with missing months risky for a monthly lag?", "type": "single",
 "options": ["It is slow", "It shifts by rows, so a gap month gives the wrong value", "It changes the index type", "It sorts the data"],
 "answer": 1,
 "why": ["Speed is not the issue.", "Correct: merge on the month number instead.", "No.", "No."]}
```

```check
{"q": "Why can we not use the real sales of the test month as a feature?", "type": "single",
 "options": ["They are too large", "They are unknown: that is what we predict", "They are negative", "They are strings"],
 "answer": 1,
 "why": ["No.", "Correct.", "No.", "No."]}
```

## Why it matters

*Predict Future Sales* uses daily sales of the Russian software company **1C Company**: 60 shops, about 22,000 items, 34 months of history. You predict the **next month** (month 34) for a list of shop and item pairs. It is a very good practice for three skills that interviews test: aggregating logs to a forecast level, building lag features by merging, and handling new items.

## Goal and metric

**Task.** For each `(shop_id, item_id)` pair in `test.csv`, predict the total units sold in November 2015. The metric is **RMSE**, and the true target is **clipped to the range [0, 20]**. So you should clip your training target and your predictions to [0, 20].

| File | Columns |
|---|---|
| `sales_train.csv` | `date, date_block_num, shop_id, item_id, item_price, item_cnt_day` |
| `test.csv` | `ID, shop_id, item_id` |
| `items.csv` | `item_name, item_id, item_category_id` |
| `item_categories.csv` | `item_category_name, item_category_id` |
| `shops.csv` | `shop_name, shop_id` |
| `sample_submission.csv` | `ID, item_cnt_month` |

`date_block_num` is the month number: 0 is January 2013 and 33 is October 2015. The `date` column is text in the form `dd.mm.yyyy`. `item_cnt_day` is negative for returns. Check these facts in the Data tab.

## Data tour

```notebook
# Run this in a Kaggle notebook (Data: Predict Future Sales)
import numpy as np
import pandas as pd
import lightgbm as lgb

DATA = "/kaggle/input/competitive-data-science-predict-future-sales/"
sales = pd.read_csv(DATA + "sales_train.csv")
test = pd.read_csv(DATA + "test.csv")
items = pd.read_csv(DATA + "items.csv")

sales["date"] = pd.to_datetime(sales["date"], format="%d.%m.%Y")
print(sales.shape, test.shape)
print("months:", sales["date_block_num"].min(), "to", sales["date_block_num"].max())
print("shops:", sales["shop_id"].nunique(), "| items:", sales["item_id"].nunique())
print(sales[["item_price", "item_cnt_day"]].describe().round(1))

# Test pairs that never appear in the training sales: a cold-start problem
seen = sales[["shop_id", "item_id"]].drop_duplicates()
m = test.merge(seen, on=["shop_id", "item_id"], how="left", indicator=True)
print("test pairs never sold before:", round((m["_merge"] == "left_only").mean(), 2))
print("test items never sold anywhere:", round((~test["item_id"].isin(sales["item_id"])).mean(), 2))
```

What to look for: very large `item_cnt_day` values (outliers), a negative price, returns, and a **large share of test pairs without history**. Remove the obvious outliers.

```notebook
sales = sales[(sales["item_price"] > 0) & (sales["item_cnt_day"] < 1000)]
```

## Baseline and validation

- **Validation:** the last known month (block 33) is the target. Train on months before it. The test month 34 has the same relation to month 33.
- **Baseline 1:** predict 0. **Baseline 2:** predict last month's clipped count for the pair (0 if none).

```chart
{"title": "Clipping the monthly total to [0, 20]: a few big sellers are capped", "x": "pair rank", "height": 210,
 "series": [
   {"name": "monthly units (raw)", "kind": "bar", "x": [1,2,3,4,5,6,7,8], "y": [60, 35, 22, 12, 8, 5, 2, 1]},
   {"name": "clipped to 20", "kind": "bar", "x": [1,2,3,4,5,6,7,8], "y": [20, 20, 20, 12, 8, 5, 2, 1]}
 ],
 "caption": "The metric clips the true target at 20, so predicting 60 for the top pair would only add error."}
```

```check
{"q": "A pair sold 45 units in the month. What is its target value for this competition?", "type": "numeric",
 "answer": 20, "tol": 0, "why": "The target is clipped to the range [0, 20], so 45 becomes 20."}
```

## Build the monthly table

Do three things: (1) build a **grid** of the pairs per month, (2) sum the sales and clip, (3) add the test month as block 34. The grid contains, for each month, all combinations of shops active that month and items sold that month. Pairs with no sale have target 0.

```notebook
keys = ["date_block_num", "shop_id", "item_id"]
grid = []
for b in range(34):
    s = sales.loc[sales["date_block_num"] == b]
    idx = pd.MultiIndex.from_product([[b], s["shop_id"].unique(), s["item_id"].unique()], names=keys)
    grid.append(idx.to_frame(index=False))
grid.append(test[["shop_id", "item_id"]].assign(date_block_num=34)[keys])     # the month to predict
df = pd.concat(grid, ignore_index=True)

monthly = (sales.groupby(keys)["item_cnt_day"].sum().clip(0, 20)               # clip the monthly total
           .rename("target").reset_index())
df = df.merge(monthly, on=keys, how="left")
df.loc[df["date_block_num"] < 34, "target"] = df.loc[df["date_block_num"] < 34, "target"].fillna(0)
print(df.shape, "| share of zero targets:", round(float((df["target"] == 0).mean()), 2))
```

The mini problem [[problem:monthly-clip-lag]] is this step in small, including the lag.

## Features

Rules for monthly lags: for month `b` use only months `b-1`, `b-2`, ... (all known when you predict month 34 from month 33).

- **Lags of the target:** 1, 2, 3, 6, 12 months.
- **Mean encodings:** average target of the item (over all shops) and of the shop (over all items) in the previous month.
- **Item age:** months since the item's first sale. New items behave differently.
- **Calendar:** month of the year.
- **Categories:** `item_category_id`, `shop_id`, `item_id`.

```notebook
def add_lag(frame, source, name, lag):
    tmp = source.copy()
    tmp["date_block_num"] += lag                              # month b of tmp becomes month b + lag
    return frame.merge(tmp.rename(columns={tmp.columns[-1]: name}), on=tmp.columns[:-1].tolist(), how="left")

for lag in (1, 2, 3, 6, 12):
    df = add_lag(df, df[keys + ["target"]], f"lag_{lag}", lag)

item_mean = df.groupby(["date_block_num", "item_id"])["target"].mean().rename("item_mean").reset_index()
shop_mean = df.groupby(["date_block_num", "shop_id"])["target"].mean().rename("shop_mean").reset_index()
df = add_lag(df, item_mean, "item_mean_lag1", 1)
df = add_lag(df, shop_mean, "shop_mean_lag1", 1)

first_month = sales.groupby("item_id")["date_block_num"].min().rename("first_month").reset_index()
df = df.merge(first_month, on="item_id", how="left")
df["item_age"] = df["date_block_num"] - df["first_month"]      # NaN or negative: not sold yet
df["month"] = df["date_block_num"] % 12
df = df.merge(items[["item_id", "item_category_id"]], on="item_id", how="left")

features = ["shop_id", "item_id", "item_category_id", "month", "item_age", "lag_1", "lag_2", "lag_3", "lag_6",
            "lag_12", "item_mean_lag1", "shop_mean_lag1"]
```

Caution: `item_mean` for month `b` is computed from month `b`'s targets, but we only use its **lag 1**, so there is no leakage. `first_month` uses the whole history: for training rows far in the past this is a small leak. For a strict version compute it only from months before `b`.

```check
{"q": "You add the feature `item_mean` of the SAME month to the training rows. Why is this leakage?", "type": "single",
 "options": ["It is a lag", "It averages the target of the month you want to predict, so it contains the answer", "It has missing values", "It is categorical"],
 "answer": 1,
 "why": ["A lag would use an earlier month.", "Correct: for the test month these values do not exist.", "Missing values are not leakage.", "Type is not the issue."]}
```

## Model, validation and error analysis

```notebook
VAL = 33
train_idx = (df["date_block_num"] >= 12) & (df["date_block_num"] < VAL)       # months with a full 12-month lag
val_idx = df["date_block_num"] == VAL

params = dict(n_estimators=1000, learning_rate=0.05, num_leaves=63, min_child_samples=50,
              subsample=0.8, subsample_freq=1, colsample_bytree=0.8, n_jobs=-1, random_state=42, verbose=-1)
model = lgb.LGBMRegressor(**params)
model.fit(df.loc[train_idx, features], df.loc[train_idx, "target"],
          eval_set=[(df.loc[val_idx, features], df.loc[val_idx, "target"])], eval_metric="rmse",
          callbacks=[lgb.early_stopping(50, verbose=False), lgb.log_evaluation(0)])
best_iter = model.best_iteration_

v = df.loc[val_idx].copy()
v["pred"] = np.clip(model.predict(v[features]), 0, 20)
rmse = lambda a, b: float(np.sqrt(np.mean((a - b) ** 2)))
print("RMSE zeros      :", round(rmse(v["target"], 0.0), 4))
print("RMSE last month :", round(rmse(v["target"], v["lag_1"].fillna(0)), 4))
print("RMSE LightGBM   :", round(rmse(v["target"], v["pred"]), 4))

# Error analysis: pairs without any sale in the last 12 months vs the others
hist = v[["lag_1", "lag_2", "lag_3", "lag_6", "lag_12"]].notna().any(axis=1)
v["has_history"] = hist
for flag, g in v.groupby("has_history"):
    print("has history =", flag, "| rows:", len(g), "| RMSE:", round(rmse(g["target"], g["pred"]), 4))
```

Questions to ask: is the error larger for pairs without history? For which categories? Is the model too low for the top sellers (they are capped at 20)? One idea: add category-level lag means, which help new items.

## Submission

```notebook
final = lgb.LGBMRegressor(**{**params, "n_estimators": int(best_iter * 1.1)})
tr = (df["date_block_num"] >= 12) & (df["date_block_num"] <= 33)
final.fit(df.loc[tr, features], df.loc[tr, "target"])

t = df[df["date_block_num"] == 34].copy()
t["item_cnt_month"] = np.clip(final.predict(t[features]), 0, 20)
sub = test.merge(t[["shop_id", "item_id", "item_cnt_month"]], on=["shop_id", "item_id"], how="left")
assert sub["item_cnt_month"].notna().all() and len(sub) == len(test)
sub[["ID", "item_cnt_month"]].to_csv("submission.csv", index=False)
print(sub.head())
```

## Worked example

The same ideas in the browser: sale lines for two shops, monthly sums with clipping, and the previous-month lag, using the logic of the mini problem.

```python
import numpy as np
import pandas as pd

rng = np.random.default_rng(5)
rows = []
for b in range(6):
    for shop in (1, 2):
        for item in (10, 11):
            for _ in range(rng.integers(0, 5)):
                rows.append((b, shop, item, int(rng.integers(-1, 12))))
lines = pd.DataFrame(rows, columns=["date_block_num", "shop_id", "item_id", "item_cnt_day"])

keys = ["date_block_num", "shop_id", "item_id"]
m = lines.groupby(keys, as_index=False)["item_cnt_day"].sum().rename(columns={"item_cnt_day": "target"})
m["target"] = m["target"].clip(0, 20).astype(float)

prev = m.rename(columns={"target": "lag_1"}).assign(date_block_num=lambda x: x["date_block_num"] + 1)
m = m.merge(prev, on=keys, how="left").fillna({"lag_1": 0.0})

last = m[m["date_block_num"] == 5]
print(last.to_string(index=False))
print("RMSE zeros:", round(float(np.sqrt((last["target"] ** 2).mean())), 3))
print("RMSE last month:", round(float(np.sqrt(((last["target"] - last["lag_1"]) ** 2).mean())), 3))
# Output:
#  date_block_num  shop_id  item_id  target  lag_1
#               5        1       11    20.0   16.0
#               5        2       10    20.0    0.0
#               5        2       11     7.0    7.0
# RMSE zeros: 16.823
# RMSE last month: 11.776
```

Even on this random data, last month's value is a better guess than zero (11.8 against 16.8). In real data many pairs repeat from month to month, which is why lag features matter.

## Common mistakes

- Clipping each daily row and not the monthly total.
- Using `shift` on monthly rows with gaps, instead of merging on the month number.
- Mean encodings of the same month (leakage).
- Training on months where the 12-month lag does not exist and not noticing the NaN.
- Predicting values outside [0, 20].
- Ignoring new items and shops in the test month.
- Keeping outliers like one row with 2,000 units.

## Interview lens

**Typical question:** "You get transaction logs and must forecast next month's units per shop and item. How do you proceed?"

**Strong answer:** "I aggregate the log to the forecast level: month, shop, item. I clip the monthly total to the metric range. I build a grid, so zero sales are explicit, and I add lag features by merging on the month number, never with row shifts. I add item and shop mean encodings from the previous month only. I validate on the last known month and compare with zeros and last month's value. I look at cold-start pairs separately, and I consider category-level features for them."

**Red flags:** random split; same-month mean encodings; no cold-start thinking; no clipping.

## Real world

- This competition was made by 1C Company and the Yandex School of Data Analysis for a Coursera course, "How to Win a Data Science Competition". It is still open for practice, and many public notebooks use gradient boosting and lag features.
- The task shows a common business pattern: logs are daily, but the decision (stocking) is monthly, so you must aggregate before you model.

## Key points

- Aggregate sale lines to monthly counts per shop and item, then clip the total to [0, 20].
- Lags come from merging on `date_block_num + lag`, not from row shifts.
- Mean encodings must use previous months only.
- Validate on the last known month and compare with zeros and last month's value.
- Many test pairs are new: analyse them separately.
