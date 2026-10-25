---
id: s15-04-m5-accuracy-wrmsse
title: M5 Forecasting - Accuracy (Walmart, hierarchy, WRMSSE, LightGBM)
minutes: 55
level: intermediate
goals: [Describe the M5 data and its 12 aggregation levels, Compute RMSSE and revenue weights by hand, Build a global LightGBM model with tweedie loss and 28-day lags, Create a submission in the F1 to F28 format]
prereqs: [s15-03-store-sales-features-model-submission]
tags: [kaggle, m5, walmart, WRMSSE, lightgbm, tweedie, hierarchy]
skills: [metrics, scale, leakage]
---

## Warm-up

```check
{"q": "Why can a feature for a 28-day forecast not use lag 7 for every forecast day?", "type": "single",
 "options": ["Lag 7 is too old", "For forecast days after day 7, lag 7 falls inside the unknown period", "Lag 7 is not a number", "It is slower"],
 "answer": 1,
 "why": ["It is recent, not old.", "Correct: you need lags of at least the horizon for a direct model.", "It is a number.", "Speed is not the issue."]}
```

```check
{"q": "What does a mean squared error loss assume about the target?", "type": "single",
 "options": ["Counts with many zeros", "Roughly symmetric errors around the mean", "Only positive values", "Only integers"],
 "answer": 1,
 "why": ["Counts with many zeros are better handled by Poisson or tweedie.", "Correct: squared error fits symmetric noise best.", "Not required.", "Not required."]}
```

## Why it matters

The M5 competition (2020) is the largest public test of retail forecasting: sales of Walmart products in three US states. The metric is unusual (WRMSSE), the data is **hierarchical**, and most series are **intermittent** (many zero days). The winning solutions used LightGBM, a gradient boosting library, with lag features. If you understand this competition, you understand most retail forecasting interviews.

## Goal and data

**Task.** Forecast unit sales for **28 days** for **3,049 products** in **10 stores** (30,490 bottom series) in California, Texas and Wisconsin.

| File | What is in it |
|---|---|
| `sales_train_validation.csv` | One row per product-store: `id, item_id, dept_id, cat_id, store_id, state_id`, then columns `d_1 ... d_1913` with daily unit sales |
| `calendar.csv` | `date, wm_yr_wk, weekday, wday, month, year, d, event_name_1, event_type_1, event_name_2, event_type_2, snap_CA, snap_TX, snap_WI` |
| `sell_prices.csv` | `store_id, item_id, wm_yr_wk, sell_price` (weekly price) |
| `sample_submission.csv` | `id` plus `F1 ... F28`; rows for `_validation` and `_evaluation` |

Notes: sales are in a **wide** format (one column per day). `snap_*` marks days when food-assistance (SNAP) purchases are allowed in that state. A product has a price only after it appears in a store. If you are not sure about a column name, check the Data tab.

## The hierarchy and the metric

The 30,490 bottom series add up to higher levels. The metric scores **12 levels** (42,840 series in total).

| Levels | Series |
|---|---|
| Total | 1 |
| State; Store; Category; Department | 3; 10; 3; 7 |
| State x category; State x department | 9; 21 |
| Store x category; Store x department | 30; 70 |
| Product; Product x state; Product x store | 3,049; 9,147; 30,490 |

**RMSSE** for one series: the square root of the forecast MSE divided by the in-sample one-step naive MSE:

`RMSSE = sqrt( mean over h of (y[h] − f[h])² / mean over t of (y[t] − y[t−1])² )`

The scale starts at the first non-zero sale of the series. Below 1 means better than the naive forecast.

**WRMSSE** is the weighted mean of RMSSE over all series: `sum of w_i × RMSSE_i`, divided by 12 levels. The weight `w_i` is the share of the series' **dollar sales** (units x price) in the last 28 days of the training data, inside its level. Big-money series matter more. Practise both parts in [[problem:wrmsse-weights-rmsse]].

```chart
{"title": "An intermittent series: most days are zero (counts of units per day)", "x": "day", "height": 200,
 "series": [
   {"name": "units sold", "kind": "bar", "x": [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21], "y": [0,0,1,0,0,0,2,0,0,1,0,0,0,0,3,0,0,0,1,0,0]}
 ],
 "caption": "Mean squared error on such data pushes forecasts toward a small positive number. A loss made for counts, like tweedie, fits better."}
```

```check
{"q": "Two series have the same RMSSE of 0.9. Series A has 50% of its level's dollar sales and series B has 1%. Which one moves WRMSSE more when you improve it?", "type": "single",
 "options": ["B, because it is smaller", "A, because its weight is much larger", "Both equally", "Neither"],
 "answer": 1,
 "why": ["Small weight means small effect.", "Correct: WRMSSE multiplies RMSSE by the weight.", "Weights differ.", "Both matter, A more."]}
```

## Baseline and validation

Baseline: repeat the **last 28 days** (this keeps the weekly pattern, as 28 is a multiple of 7). Validation: hold out the last 28 known days (`d_1886 ... d_1913`), train on the days before, and score with the weighted RMSSE. The code below scores only the bottom level, which is a close but incomplete proxy for the full 12-level metric.

```notebook
# Run this in a Kaggle notebook (Data: M5 Forecasting - Accuracy)
import numpy as np
import pandas as pd
import lightgbm as lgb

DATA = "/kaggle/input/m5-forecasting-accuracy/"
calendar = pd.read_csv(DATA + "calendar.csv", parse_dates=["date"])
sales = pd.read_csv(DATA + "sales_train_validation.csv")
prices = pd.read_csv(DATA + "sell_prices.csv")
sample = pd.read_csv(DATA + "sample_submission.csv")

id_cols = ["id", "item_id", "dept_id", "cat_id", "store_id", "state_id"]
d_cols = [c for c in sales.columns if c.startswith("d_")]
n_days, H = len(d_cols), 28                               # 1913 days in the real data
print(sales.shape, "| days:", n_days)
print("share of zero cells:", round(float((sales[d_cols].to_numpy() == 0).mean()), 2))
print(sales.groupby("state_id")["id"].count())

# Bottom-level proxy of the metric: revenue-weighted RMSSE
Y = sales[d_cols].to_numpy(dtype=np.float32)               # shape (series, days)
mean_price = prices.groupby(["store_id", "item_id"])["sell_price"].mean()
price_vec = pd.MultiIndex.from_frame(sales[["store_id", "item_id"]]).map(mean_price).to_numpy(dtype=float)
price_vec = np.nan_to_num(price_vec)

def wrmsse_bottom(train_Y, actual, pred, weights_units):
    """train_Y: (series, T); actual, pred: (series, H); weights from units of the last 28 train days."""
    scales = np.empty(len(train_Y))
    for i, row in enumerate(train_Y):
        nz = np.nonzero(row)[0]
        r = row[nz[0]:] if len(nz) else row[:0]
        scales[i] = np.mean(np.diff(r) ** 2) if len(r) > 1 else np.nan
    ok = scales > 0
    rmsse = np.sqrt(np.mean((actual - pred) ** 2, axis=1)[ok] / scales[ok])
    w = weights_units[ok] * price_vec[ok]
    return float(np.sum(w / w.sum() * rmsse))

train_Y, valid_Y = Y[:, :-H], Y[:, -H:]
w_units = train_Y[:, -H:].sum(axis=1)                      # units sold in the last 28 train days
naive = train_Y[:, -H:]                                    # repeat the last 28 days
print("WRMSSE (bottom level) repeat last 28 days:", round(wrmsse_bottom(train_Y, valid_Y, naive, w_units), 4))
print("WRMSSE (bottom level) all zeros:          ", round(wrmsse_bottom(train_Y, valid_Y, np.zeros_like(valid_Y), w_units), 4))
```

## Features

We use the **direct strategy** again: every feature ends at least 28 days before the target. First convert the wide table to a long one for the last 730 days (all 1913 days need much more memory), then add the 28 future days.

```notebook
KEEP = 730                                                  # use fewer days if the notebook runs out of memory
keep_cols = d_cols[-KEEP:]
long = sales[id_cols + keep_cols].melt(id_vars=id_cols, var_name="d", value_name="sales")
future = pd.concat([sales[id_cols].assign(d=f"d_{n_days + k}", sales=np.nan) for k in range(1, H + 1)])
df = pd.concat([long, future], ignore_index=True)
df["d_num"] = df["d"].str[2:].astype(int)

# Calendar and SNAP (food-assistance) flag of the row's state
cal_cols = ["d", "date", "wm_yr_wk", "wday", "month", "year", "event_name_1", "event_type_1", "snap_CA", "snap_TX", "snap_WI"]
df = df.merge(calendar[cal_cols], on="d", how="left")
df["snap"] = np.select([df["state_id"] == "CA", df["state_id"] == "TX", df["state_id"] == "WI"],
                       [df["snap_CA"], df["snap_TX"], df["snap_WI"]], default=0)
df = df.drop(columns=["snap_CA", "snap_TX", "snap_WI"])

# Prices: a missing price means the product is not on sale yet in that store
df = df.merge(prices, on=["store_id", "item_id", "wm_yr_wk"], how="left")
df["price_rel"] = df["sell_price"] / df.groupby(["store_id", "item_id"])["sell_price"].transform("mean")

# Lag and rolling features, all ending at least H = 28 days before the target day
df = df.sort_values(["id", "d_num"]).reset_index(drop=True)
g = df.groupby("id")["sales"]
for k in (28, 35, 42):
    df[f"lag_{k}"] = g.shift(k)
shifted = g.shift(H)
for w in (7, 28):
    df[f"rmean_{w}"] = shifted.groupby(df["id"]).rolling(w, min_periods=1).mean().reset_index(level=0, drop=True)

for c in ["item_id", "dept_id", "cat_id", "store_id", "state_id", "event_name_1", "event_type_1"]:
    df[c] = df[c].astype("category")
features = ["item_id", "dept_id", "cat_id", "store_id", "state_id", "wday", "month", "snap", "event_name_1",
            "event_type_1", "sell_price", "price_rel", "lag_28", "lag_35", "lag_42", "rmean_7", "rmean_28"]
print(df.shape)
```

## Model: a tweedie loss

Unit sales are **non-negative counts** with many zeros and a few large values. A **tweedie** loss (`objective="tweedie"`) models this kind of data. Its power parameter `tweedie_variance_power` is between 1 and 2. A value near 1 is like Poisson. Many M5 solutions used values around 1.1 to 1.2. It is a setting to tune on validation.

```notebook
valid_first = n_days - H + 1                                # first validation day number
usable = df["sales"].notna() & df["sell_price"].notna()     # skip rows before the product was on sale
fit_idx = usable & (df["d_num"] < valid_first)
val_idx = usable & (df["d_num"] >= valid_first) & (df["d_num"] <= n_days)

params = dict(objective="tweedie", tweedie_variance_power=1.1, n_estimators=1500, learning_rate=0.05,
              num_leaves=63, min_child_samples=50, subsample=0.8, subsample_freq=1, colsample_bytree=0.8,
              n_jobs=-1, random_state=42, verbose=-1)
model = lgb.LGBMRegressor(**params)
model.fit(df.loc[fit_idx, features], df.loc[fit_idx, "sales"],
          eval_set=[(df.loc[val_idx, features], df.loc[val_idx, "sales"])], eval_metric="rmse",
          callbacks=[lgb.early_stopping(50, verbose=False), lgb.log_evaluation(0)])
best_iter = model.best_iteration_
print("best number of trees:", best_iter)

# Score with the bottom-level proxy of WRMSSE (rows without a price are predicted as 0)
vdf = df[(df["d_num"] >= valid_first) & (df["d_num"] <= n_days)].copy()
vdf["pred"] = 0.0
has_price = vdf["sell_price"].notna()
vdf.loc[has_price, "pred"] = np.clip(model.predict(vdf.loc[has_price, features]), 0, None)
pred_wide = vdf.pivot(index="id", columns="d_num", values="pred").reindex(sales["id"]).to_numpy()
print("WRMSSE (bottom level) LightGBM:", round(wrmsse_bottom(train_Y, valid_Y, pred_wide, w_units), 4))
```

Compare the number with the "repeat last 28 days" baseline. Then look at the errors: which departments or stores are worst? Is the model too high on intermittent items? Try `tweedie_variance_power` of 1.05 to 1.3, and more lags.

```check
{"q": "Why is a tweedie (or Poisson-like) loss often better than squared error for M5 unit sales?", "type": "single",
 "options": ["It is faster", "Sales are non-negative counts with many zeros, and the loss fits that distribution", "It removes holidays", "It works only with GPU"],
 "answer": 1,
 "why": ["Speed is not the reason.", "Correct.", "It does not handle holidays.", "It runs on CPU."]}
```

## Submission

The submission has one row per `id` with columns `F1 ... F28`. Rows ending in `_validation` are scored first. Rows ending in `_evaluation` are for the later stage. We train on all known days and fill both parts with the same forecasts, as a simple start.

```notebook
final = lgb.LGBMRegressor(**{**params, "n_estimators": int(best_iter * 1.1)})
final.fit(df.loc[usable & (df["d_num"] <= n_days), features], df.loc[usable & (df["d_num"] <= n_days), "sales"])

fdf = df[df["d_num"] > n_days].copy()
fdf["pred"] = 0.0
hp = fdf["sell_price"].notna()
fdf.loc[hp, "pred"] = np.clip(final.predict(fdf.loc[hp, features]), 0, None)
fdf["h"] = fdf["d_num"] - n_days
wide = fdf.pivot(index="id", columns="h", values="pred")
wide.columns = [f"F{h}" for h in wide.columns]
wide = wide.reset_index()                                   # column: id (ends with _validation)

sub = sample[["id"]].copy()
sub["key"] = sub["id"].str.replace("_evaluation", "_validation")
sub = sub.merge(wide, left_on="key", right_on="id", how="left", suffixes=("", "_w")).drop(columns=["key", "id_w"])
sub = sub.fillna(0.0)
sub.to_csv("submission.csv", index=False)
print(sub.shape, list(sub.columns[:4]))
```

## Worked example

A tiny hierarchy in the browser: two stores, two products each (four bottom series). We compute revenue weights for two levels (total and bottom), the RMSSE of every series, and a WRMSSE from the two levels. The real metric uses 12 levels.

```python
import numpy as np
import pandas as pd

rng = np.random.default_rng(2)
T, H = 60, 7
keys = [("S1", "A"), ("S1", "B"), ("S2", "A"), ("S2", "B")]
mean = [8, 1, 5, 0.5]
Y = np.array([rng.poisson(m, T + H) for m in mean], dtype=float)
train, actual = Y[:, :T], Y[:, T:]
pred = train[:, -7:]                                   # repeat the last 7 days (the "naive" forecast)
price = np.array([2.0, 10.0, 2.0, 10.0])
revenue = train[:, -28:].sum(axis=1) * price           # dollar sales in the last 28 days

def rmsse(tr, a, f):
    nz = np.nonzero(tr)[0]
    r = tr[nz[0]:]
    scale = np.mean(np.diff(r) ** 2)
    return float(np.sqrt(np.mean((a - f) ** 2) / scale))

# level 1: total (1 series); level 2: bottom (4 series)
total_tr, total_a, total_f = train.sum(0), actual.sum(0), pred.sum(0)
lvl_total = 1.0 * rmsse(total_tr, total_a, total_f)
w = revenue / revenue.sum()
lvl_bottom = sum(w[i] * rmsse(train[i], actual[i], pred[i]) for i in range(4))

print("weights bottom:", np.round(w, 3).tolist())
print("RMSSE total:", round(lvl_total, 3))
print("weighted RMSSE bottom:", round(lvl_bottom, 3))
print("WRMSSE (2 levels):", round((lvl_total + lvl_bottom) / 2, 3))
# Output:
```

The expensive items (price 10) get higher weights even when they sell fewer units. The total level is easier (smaller RMSSE) because noise cancels when you add series.

## Common mistakes

- Using squared error loss on very sparse counts without thinking about tweedie or Poisson.
- Features with lags shorter than 28 days for a direct 28-day model.
- Ignoring that a missing price means the product is not on sale.
- Running out of memory by melting all 1913 days with float64.
- Looking only at the bottom level; the metric rewards good aggregate forecasts too.
- Forgetting the `_evaluation` rows in the submission.
- Using the same weights for all levels instead of weights within each level.

## Interview lens

**Typical question:** "How would you forecast 30,000 intermittent product-store series with a hierarchy?"

**Strong answer:** "I use one global gradient boosting model with a count-friendly loss such as tweedie, because most series are sparse and share patterns by department, store and calendar. Features are lags and rolling means that end at least the horizon before the target, price features, calendar and event features. I validate on the last 28 days with the competition metric, WRMSSE, which weights series by revenue and scales errors by each series' history. I check the aggregate levels too, and I would consider reconciliation if aggregates look inconsistent."

**Red flags:** MAPE on intermittent data; per-series ARIMA for 30,000 series; ignoring the metric's weights.

## Real world

- The M5 competition was run by the University of Nicosia (the M-competitions team) on Kaggle in 2020, with Walmart data. It had an Accuracy track (point forecasts, WRMSSE) and an Uncertainty track (quantiles).
- Top solutions in the Accuracy track used LightGBM with lag and price features, often with several models averaged. Read the M5 results paper by Makridakis, Spiliotis and Assimakopoulos in the International Journal of Forecasting.

## Key points

- M5: 30,490 bottom series, 12 hierarchy levels, 28-day horizon, metric WRMSSE.
- RMSSE scales error by the series' own one-step naive error from its first sale; weights come from recent dollar sales.
- Direct LightGBM with lags of at least 28 days, price, calendar and SNAP features, and a tweedie loss.
- Validate on the last 28 days; check aggregate levels; the submission needs F1 to F28 for both validation and evaluation ids.
