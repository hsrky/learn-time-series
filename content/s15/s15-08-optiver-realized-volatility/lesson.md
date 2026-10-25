---
id: s15-08-optiver-realized-volatility
title: Optiver Realized Volatility Prediction - order books, WAP and RMSPE
minutes: 50
level: intermediate
goals: [Explain the order book, WAP, log returns and realized volatility, Compute volatility features from book and trade data, Build a validation that does not leak between stocks, Train LightGBM with weights that optimise RMSPE]
prereqs: [s15-06-rossmann-store-sales]
tags: [kaggle, optiver, volatility, order-book, WAP, RMSPE, finance]
skills: [metrics, leakage, from-scratch]
---

## Warm-up

```check
{"q": "What does RMSPE measure?", "type": "single",
 "options": ["Absolute error in units", "Square root of the mean of squared percentage errors", "Bias only", "Error on a log scale only"],
 "answer": 1,
 "why": ["That is MAE or RMSE.", "Correct.", "Bias is different.", "That is RMSLE."]}
```

```check
{"q": "Why can a random row split leak information when rows from different groups share the same time?", "type": "single",
 "options": ["It cannot", "Rows at the same time carry related information, so the model sees the future of its neighbours", "It makes training slower", "It removes outliers"],
 "answer": 1,
 "why": ["It can.", "Correct: split by the time group, not by row.", "Not the issue.", "No."]}
```

## Why it matters

*Optiver Realized Volatility Prediction* (2021) came from a market-making firm. **Volatility** measures how much a price moves. Firms that quote buy and sell prices need to know it, because a risky stock needs wider prices. The data is high-frequency: snapshots of the **order book** every second. You predict the volatility of the next 10 minutes. It shows two interview themes: feature engineering from raw event data, and a validation that respects hidden structure.

## Goal, data and metric

**Task.** For each stock and each 10-minute window (`time_id`), use the first 10 minutes of data. Predict the **realized volatility of the next 10 minutes** (the `target`). There are about 112 stocks.

| File | Content |
|---|---|
| `train.csv` | `stock_id, time_id, target` |
| `book_train.parquet/stock_id=<n>/` | order-book snapshots: `time_id, seconds_in_bucket, bid_price1, ask_price1, bid_price2, ask_price2, bid_size1, ask_size1, bid_size2, ask_size2` |
| `trade_train.parquet/stock_id=<n>/` | trades: `time_id, seconds_in_bucket, price, size, order_count` |
| `test.csv` | `stock_id, time_id, row_id` (hidden data; a code competition) |

An **order book** lists the offers to buy (bids) and to sell (asks). `bid_price1` is the best (highest) bid. `ask_price1` is the best (lowest) ask. Level 2 is the next best. `seconds_in_bucket` is the time in the 10-minute window (0 to 599). Check the Data tab for the exact folder names and the way the test is served.

**Metric: RMSPE** (as in Rossmann): `sqrt(mean(((y − p) / y)²))`. Volatility is positive, so there is no zero problem.

Two notes: `time_id` values are not in chronological order (they were shuffled), so you cannot use "the previous window". And different stocks share the same `time_id`: the same real time period.

## Volatility from an order book

1. **WAP** (weighted average price): `(bid_price1 × ask_size1 + ask_price1 × bid_size1) / (bid_size1 + ask_size1)`. It moves toward the side with the smaller size, where the price is likely to move.
2. **Log return** between snapshots: `r_t = log(WAP_t) − log(WAP_{t−1})`.
3. **Realized volatility**: `RV = sqrt(Σ r_t²)` inside the window.

The simplest model says "the next 10 minutes will be as volatile as the last 10 minutes". That means you predict the RV of the input window. It is a strong baseline. Build it in [[problem:wap-realized-volatility]].

```chart
{"title": "A price with calm and busy periods: the size of the changes (volatility) varies", "x": "second", "height": 230,
 "series": [
   {"name": "price", "gen": [["randomWalk", {"sd": 0.3, "start": 100}]], "n": 120, "seed": 11}
 ],
 "caption": "Volatility is the typical size of the steps, not the direction. Realized volatility sums the squared steps."}
```

```check
{"q": "WAPs of 100, 101, 100 give log returns of about +0.00995 and −0.00995. What is the realized volatility (sqrt of the sum of squares)?", "type": "numeric",
 "answer": 0.01407, "tol": 0.0002, "why": "Squares: 0.000099 each, sum 0.000198, square root 0.01407."}
```

## Data tour and baseline

```notebook
# Run this in a Kaggle notebook (Data: Optiver Realized Volatility Prediction)
import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import GroupKFold

DATA = "/kaggle/input/optiver-realized-volatility-prediction/"
train = pd.read_csv(DATA + "train.csv")
print(train.shape, "| stocks:", train["stock_id"].nunique(), "| windows:", train["time_id"].nunique())
print(train["target"].describe().round(5))

sid = int(train["stock_id"].iloc[0])
book = pd.read_parquet(DATA + f"book_train.parquet/stock_id={sid}")
trade = pd.read_parquet(DATA + f"trade_train.parquet/stock_id={sid}")
print(book.head(3))
print("book rows per window:", round(book.groupby("time_id").size().mean(), 1),
      "| trade rows per window:", round(trade.groupby("time_id").size().mean(), 1))
```

Check three things. How many snapshots does a window have (not every second has one)? What is the range of the target? How do sizes and spreads differ between stocks?

## Features

For each window we compute one row of features. Everything uses only the input window.

```notebook
def rv(x):
    return float(np.sqrt(np.sum(np.square(x))))

def book_features(book):
    d = book.sort_values(["time_id", "seconds_in_bucket"]).copy()
    d["wap"] = (d["bid_price1"] * d["ask_size1"] + d["ask_price1"] * d["bid_size1"]) / (d["bid_size1"] + d["ask_size1"])
    d["log_ret"] = np.log(d["wap"]).groupby(d["time_id"]).diff()                    # return inside each window
    d["ret2"] = d["log_ret"] ** 2
    d["spread"] = (d["ask_price1"] - d["bid_price1"]) / d["wap"]
    d["imbalance"] = (d["bid_size1"] - d["ask_size1"]) / (d["bid_size1"] + d["ask_size1"])
    d["depth"] = d["bid_size1"] + d["ask_size1"] + d["bid_size2"] + d["ask_size2"]
    f = d.groupby("time_id").agg(rv_full=("ret2", lambda s: float(np.sqrt(s.sum()))),
                                 spread_mean=("spread", "mean"), imbalance_abs=("imbalance", lambda s: float(s.abs().mean())),
                                 depth_mean=("depth", "mean"), n_book=("wap", "size"))
    for start in (150, 300, 450):                       # volatility of the later part of the window
        late = d[d["seconds_in_bucket"] >= start].groupby("time_id")["ret2"].sum().pow(0.5).rename(f"rv_{start}")
        f = f.join(late)
    return f.reset_index()

def trade_features(trade):
    f = trade.groupby("time_id").agg(trade_volume=("size", "sum"), trade_orders=("order_count", "sum"),
                                     n_trades=("price", "size"))
    return f.reset_index()

parts = []
for sid in sorted(train["stock_id"].unique())[:20]:         # first 20 stocks to keep the run short
    b = pd.read_parquet(DATA + f"book_train.parquet/stock_id={sid}")
    t = pd.read_parquet(DATA + f"trade_train.parquet/stock_id={sid}")
    f = book_features(b).merge(trade_features(t), on="time_id", how="left")
    f["stock_id"] = sid
    parts.append(f)
feat = pd.concat(parts, ignore_index=True)
data = train.merge(feat, on=["stock_id", "time_id"], how="inner").fillna({"trade_volume": 0, "trade_orders": 0, "n_trades": 0})
for k in (150, 300, 450):
    data[f"rv_{k}"] = data[f"rv_{k}"].fillna(0.0)
print(data.shape)
```

Extra ideas:

- The same features for the level-2 prices.
- Realized volatility of trade prices.
- **Stock-level** averages of the target. Compute this target encoding inside the training folds only.
- **Time-level** features, such as the mean of `rv_full` across all stocks in the same `time_id`. This is the market-wide volatility, and it is a strong signal.

## Validation: group by time_id

The same `time_id` is the same real period for all stocks. Volatility is strongly related across stocks at the same time. Suppose one stock's window is in training. Another stock's window from the same `time_id` is in validation. The model can then learn the market mood of that period. In the real test, the periods are new. So validate with **groups by `time_id`**.

```notebook
data["rv_market"] = data.groupby("time_id")["rv_full"].transform("mean")        # market-wide volatility of the window
features = ["stock_id", "rv_full", "rv_150", "rv_300", "rv_450", "spread_mean", "imbalance_abs",
            "depth_mean", "n_book", "trade_volume", "trade_orders", "n_trades", "rv_market"]

def rmspe(y, p):
    return float(np.sqrt(np.mean(((y - p) / y) ** 2)))

print("RMSPE baseline (next volatility = this window's volatility):", round(rmspe(data["target"], data["rv_full"]), 4))

oof = np.zeros(len(data))
gkf = GroupKFold(n_splits=5)
for fold, (tr_i, va_i) in enumerate(gkf.split(data, groups=data["time_id"])):
    X_tr, y_tr = data.iloc[tr_i][features], data.iloc[tr_i]["target"]
    X_va, y_va = data.iloc[va_i][features], data.iloc[va_i]["target"]
    model = lgb.LGBMRegressor(n_estimators=600, learning_rate=0.03, num_leaves=31, min_child_samples=20,
                              subsample=0.8, subsample_freq=1, colsample_bytree=0.8, n_jobs=-1,
                              random_state=fold, verbose=-1)
    model.fit(X_tr, y_tr, sample_weight=1.0 / y_tr ** 2,                     # weights turn RMSE into RMSPE
              eval_set=[(X_va, y_va)], eval_sample_weight=[1.0 / y_va ** 2],
              callbacks=[lgb.early_stopping(50, verbose=False), lgb.log_evaluation(0)])
    oof[va_i] = model.predict(X_va)
    print("fold", fold, "RMSPE:", round(rmspe(y_va, oof[va_i]), 4), "| trees:", model.best_iteration_)
print("RMSPE out-of-fold:", round(rmspe(data["target"], oof), 4))
```

**The weight trick.** RMSPE is `sqrt(mean(((y − p)/y)²))`. This equals a weighted squared error with weight `1/y²` on each row. So a normal squared-error LightGBM with `sample_weight = 1 / y²` optimises RMSPE directly.

```check
{"q": "Why is `sample_weight = 1 / y**2` with squared error the same as RMSPE?", "type": "single",
 "options": ["It is a coincidence", "Because ((y − p) / y)² = (y − p)² × (1 / y²)", "Because y is always 1", "Because RMSPE ignores errors"],
 "answer": 1,
 "why": ["It follows from algebra.", "Correct: each squared error is multiplied by 1 / y².", "y varies.", "RMSPE counts errors."]}
```

## Error analysis

```notebook
data["pred"] = oof
data["pe2"] = ((data["target"] - data["pred"]) / data["target"]) ** 2
print("--- worst stocks")
print(data.groupby("stock_id")["pe2"].mean().pow(0.5).sort_values(ascending=False).head(5).round(3))
print("--- error by volatility level")
bins = pd.qcut(data["target"], 4, labels=["low", "mid-low", "mid-high", "high"])
print(data.groupby(bins, observed=True)["pe2"].mean().pow(0.5).round(3))
print("--- baseline vs model by volatility level")
data["pe2_base"] = ((data["target"] - data["rv_full"]) / data["target"]) ** 2
print(data.groupby(bins, observed=True)[["pe2_base", "pe2"]].mean().pow(0.5).round(3))
```

Typical findings: low-volatility windows have a larger percentage error (small denominators), and some stocks are harder. Time-level features are often very useful; test them on your own folds.

## Submission (code competition)

In a **code competition** your notebook is run on hidden test data. You must train (or load) a model, build the same features for the test windows, and call the competition's API. The exact module and function names come from the starter notebook on the competition page. Copy the pattern from there.

```notebook
# Pattern only. Copy the exact API calls from the competition's starter notebook.
# 1. Train the final model on all training rows (same features as above).
# 2. For each test batch: read the book and trade parquet files, build book_features and trade_features,
#    add the market feature, predict, and write the 'target' column of the sample prediction.
# 3. The notebook must run without internet and finish within the time limit.
final = lgb.LGBMRegressor(n_estimators=600, learning_rate=0.03, num_leaves=31, subsample=0.8, subsample_freq=1,
                          colsample_bytree=0.8, n_jobs=-1, random_state=0, verbose=-1)
final.fit(data[features], data["target"], sample_weight=1.0 / data["target"] ** 2)
```

## Worked example

In the browser: a tiny order book for three windows. We compute WAP, log returns and realized volatility with the logic of the mini problem. Then we compare the "next volatility equals this volatility" baseline with a simple scaling.

```python
import numpy as np
import pandas as pd

rng = np.random.default_rng(6)
rows = []
for t, vol in [(1, 0.0003), (2, 0.0010), (3, 0.0020)]:
    n = 60
    mid = 100 * np.exp(np.cumsum(rng.normal(0, vol, n)))
    sp = 0.02
    rows.append(pd.DataFrame({"time_id": t, "seconds_in_bucket": np.arange(0, 600, 10), "bid_price1": mid - sp, "ask_price1": mid + sp,
                              "bid_size1": rng.integers(10, 100, n), "ask_size1": rng.integers(10, 100, n)}))
book = pd.concat(rows)

book["wap"] = (book["bid_price1"] * book["ask_size1"] + book["ask_price1"] * book["bid_size1"]) / (book["bid_size1"] + book["ask_size1"])
book["ret2"] = book.groupby("time_id")["wap"].transform(lambda s: np.log(s).diff()) ** 2
rv = book.groupby("time_id")["ret2"].sum().pow(0.5)
print(rv.round(5).to_string())

target = pd.Series({1: 0.0031, 2: 0.0078, 3: 0.0165})                 # made-up next-window volatility
rmspe = lambda y, p: float(np.sqrt(np.mean(((y - p) / y) ** 2)))
print("RMSPE baseline (target = this window):", round(rmspe(target, rv), 4))
print("RMSPE after scaling by 1.1:", round(rmspe(target, rv * 1.1), 4))
# Output:
# time_id
# 1    0.00234
# 2    0.00781
# 3    0.01480
# RMSPE baseline (target = this window): 0.1536
# RMSPE after scaling by 1.1: 0.1147
```

Volatility is larger when the steps are larger, as expected. The baseline is already close, and a small tuned factor improves the error. A real model adds more features, such as the market-wide volatility.

## Common mistakes

- Computing the return across the border of two windows.
- Splitting by row instead of by `time_id` (leaks market information).
- Optimising squared error without weights, while the metric is relative.
- Using the mid price when WAP is more informative.
- Ignoring that `time_id` is not chronological and building "previous window" features.
- Reading the whole data set at once and running out of memory.
- Features computed from the future part of the window that is also the target.

## Interview lens

**Typical question:** "How would you predict volatility from raw order-book data?"

**Strong answer:** "I compute the weighted average price from the best bid and ask. I take log returns inside each window. My main feature is realized volatility, the square root of the sum of squared returns. The baseline is that the next window equals this one. I add volatility of sub-windows, spread, size imbalance, depth, and trade features, plus a market-wide volatility feature per time window. I validate with groups by time id so stocks at the same time do not leak. I optimise the relative metric with squared error and weights of one over the squared target."

**Red flags:** random row split; no baseline; returns across window borders; ignoring the metric.

## Real world

- Optiver, an electronic market maker, hosted this competition in 2021. Market makers quote prices on both sides and need good volatility estimates to set spreads and manage risk.
- Realized volatility from high-frequency data is a standard tool in finance. Summing squared returns is a classic estimator. The HAR model in finance literature uses volatility over several horizons, which is similar to our sub-window features.

## Key points

- WAP combines best bid and ask by opposite sizes. Log returns are taken inside a window. Realized volatility is the square root of the sum of squared returns.
- The baseline "next window equals this window" is strong.
- Add sub-window volatility, spread, imbalance, depth, trade features, and a market-wide feature per time id.
- Validate with GroupKFold by `time_id`; use `sample_weight = 1 / y²` to optimise RMSPE.
- Code competitions run your notebook on hidden test data: build the same features there.
