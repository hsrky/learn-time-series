---
id: s5-06-global-vs-local-models
title: Global and local models
minutes: 25
level: intermediate
goals: [Explain local and global and hybrid models, Pool many series into one training table with scaling and id features, Know when a global model wins and when it fails]
prereqs: [s5-04-target-transforms-scaling, s5-05-multistep-strategies]
tags: [global-models, pooling, scale, series-id]
skills: [scale, from-scratch]
---
## Warm-up
```check
{"q": "You train on series with very different sizes. What helps most?", "type": "single",
 "options": ["Scale each series with its own training statistics", "Use the test data to compute one scaler", "Drop the large series"],
 "answer": 0,
 "why": ["Correct: all series are then in a similar range, and no test data leaks.", "That leaks the test period.", "You lose business-critical series."]}
```

```check
{"q": "Recursive or direct: which strategy trains one model per horizon step?", "type": "single",
 "options": ["Recursive", "Direct", "Neither"],
 "answer": 1,
 "why": ["Recursive uses one model many times.", "Correct: model k predicts step k.", "One of them does."]}
```

## Why it matters
A retailer has 50,000 products. Do you train 50,000 small models, or one big model? A bank has 20 years of data for one rate, and a start-up has 3 months for each new product. The answer changes the accuracy, the cost, and how you handle new items. This choice, **local or global**, is one of the most important design decisions in modern forecasting.

## Local models
A **[[local model|local]]** model is trained on **one** series and forecasts only that series. Classical methods (ETS, ARIMA) are local.

Pros: fits each series exactly; easy to explain; no need to scale or share anything.
Cons: needs enough history per series; 50,000 series mean 50,000 fits to run, monitor and fix; it cannot learn from similar series, so short series give noisy models.

## Global models
A **[[global model|global]]** model is trained on **many series at once**. We stack the windows of all series in one big table and fit one model.

Example: 1,000 series with 100 points each. With a window of 7 there are about 93 rows per series, so ~93,000 rows for one model. A local model has only ~93 rows.

Pros: much more training data; learns shared patterns (weekly season, holiday effects); works for short series and new series; one model to deploy.
Cons: needs scaling, so large series do not dominate; needs a way to separate different behaviour (id features); one model may underfit the unusual series.

```check
{"q": "1,000 series, 120 points each, window 10, horizon 1. How many rows does the global table have?", "type": "numeric",
 "answer": 110000, "tol": 0.5,
 "why": "Per series: 120 - 10 - 1 + 1 = 110 rows. Times 1,000 series = 110,000."}
```

## How to build the global table
1. **Scale per series** (log1p, then standardize, or divide by the window mean), using training data only.
2. Make windows per series. Never let a window cross from one series to the next.
3. Stack all rows. Add **[[static feature|static features]]**: series id (as a category), store type, region, product group. Add calendar features and known covariates.
4. Fit one model. Evaluate with one time cutoff for all series (the same backtest folds).
5. Invert the scale per series for the final forecast.

The **series id** feature lets a tree model learn "series 17 behaves differently". With thousands of ids, do not use one-hot. Use a native categorical feature or an [[embedding]] (a learned vector per id, used in neural networks).

```chart
{"title": "Series with different levels: scaled, they share one pattern", "x": "day", "height": 220,
 "series": [
   {"name": "small shop (scaled)", "gen": [["const", {"value": 1}], ["season", {"period": 7, "amp": 0.3}], ["noise", {"sd": 0.05}]], "n": 42, "seed": 1},
   {"name": "big shop (scaled)", "gen": [["const", {"value": 1}], ["season", {"period": 7, "amp": 0.3}], ["noise", {"sd": 0.05}]], "n": 42, "seed": 2, "dash": true}
 ],
 "caption": "Both shops have a weekly pattern. After scaling, one model can learn it from both."}
```

```check
{"q": "A global model is trained on raw sales of 5 shops. One shop is 100 times larger. What is the likely problem?", "type": "single",
 "options": ["The large shop dominates the loss, small shops are fitted badly", "The model cannot read the data", "Nothing; models are scale-free"],
 "answer": 0,
 "why": ["Correct: squared or absolute errors are in raw units, so the large shop counts most.", "The model can read it, but the fit is unbalanced.", "Most models are not scale-free."]}
```

## When to use which
| Situation | Prefer |
|---|---|
| Few long, important series, each very different | Local (or both) |
| Thousands of related series (retail, web traffic) | Global |
| Many short series or new series | Global |
| Strong shared patterns (promotions, holidays) | Global with covariates |
| Need per-series explanation for a regulator | Local |

A **hybrid** is common. Use a global model for most series. Use local models, or another global model, for groups that behave differently. Groups can be product families or sizes. Another option is to cluster series first and train one model per cluster.

```check
{"q": "A retailer launches 2,000 new products every month, each with 2 weeks of history. Which approach is more realistic?", "type": "single",
 "options": ["One ARIMA model per product", "A global model with static product features", "Wait until each product has 3 years of data"],
 "answer": 1,
 "why": ["Two weeks of data are too little to fit a stable ARIMA.", "Correct: the global model learns from older products and uses features of the new one.", "The business needs forecasts now."]}
```

## Worked example
We create 30 related series with different levels. Each has only 25 training points. We compare a local AR(3) per series with one global AR(3) trained on all series with window-mean scaling. We forecast one step on the next 5 points (using true history).

```python
import numpy as np

rng = np.random.default_rng(3)
n_series, n, p = 30, 30, 3
levels = rng.uniform(10, 200, n_series)

def ar_noise(n):
    x = np.zeros(n)
    for t in range(2, n):
        x[t] = 0.6 * x[t - 1] - 0.3 * x[t - 2] + rng.normal(0, 0.08)
    return x

Y = np.array([L * (1 + ar_noise(n)) for L in levels])      # shape (30, 30)
train_len = 25

def windows(y, p):
    X = np.array([y[i:i + p] for i in range(len(y) - p)])
    return np.c_[X, np.ones(len(X))], y[p:]

# Local: one least-squares AR(3) per series, 22 rows each
local_err = []
for y in Y:
    A, t = windows(y[:train_len], p)
    w, *_ = np.linalg.lstsq(A, t, rcond=None)
    for s in range(train_len, n):
        pred = np.r_[y[s - p:s], 1.0] @ w
        local_err.append(abs(pred - y[s]) / y[s])

# Global: divide every window and target by the window mean, pool all series
rows, targets = [], []
for y in Y:
    A, t = windows(y[:train_len], p)
    sc = A[:, :p].mean(axis=1)
    rows.append(np.c_[A[:, :p] / sc[:, None], np.ones(len(A))])   # scaled lags + intercept
    targets.append(t / sc)
G = np.vstack(rows)
w, *_ = np.linalg.lstsq(G, np.concatenate(targets), rcond=None)
global_err = []
for y in Y:
    for s in range(train_len, n):
        win = y[s - p:s]
        sc = win.mean()
        pred = (np.r_[win / sc, 1.0] @ w) * sc
        global_err.append(abs(pred - y[s]) / y[s])

print("rows per local model:", train_len - p)
print("rows in global model:", len(G))
print("local  mean abs % error:", round(100 * np.mean(local_err), 2))
print("global mean abs % error:", round(100 * np.mean(global_err), 2))
# Output:
# rows per local model: 22
# rows in global model: 660
# local  mean abs % error: 8.38
# global mean abs % error: 8.1
```

The global model sees 660 rows instead of 22, so its weights are more stable. The error is a little lower (8.1% against 8.4%). The gain is small here, because the noise dominates. It grows when each series is shorter or when the pattern is more complex.

## Common mistakes
- Training a global model on raw values of series with very different scale.
- Leaving out static features, so that the model cannot tell different series apart.
- Mixing windows across series when you build lags (`shift` without `groupby`).
- Using different cutoffs per series in the backtest. Use the same cutoff dates for all.
- Judging a global model only by the average error. Large series can hide bad results for small ones.
- Forgetting that new series need static features, because they have no id history.

## Interview lens
**Typical question:** "You must forecast 100,000 products. Do you build 100,000 models?"

**Strong answer:** I would start with a global model. It pools all series and scales each one with its own training statistics. It uses lag, rolling and calendar features, and static features such as category and store. This gives much more data per parameter, handles short and new series, and gives one model to deploy and monitor. I would still keep a simple local baseline such as seasonal naive and compare by series group. If some groups behave differently, I add group features or train a separate model for the group.

**Red flags:** "ARIMA for each of the 100,000 series" without discussing cost; global model without scaling; no baseline; no plan for new series.

## Real world
- Montero-Manso and Hyndman (2021) studied "locality and globality" for groups of series. They showed that global models can match or beat local ones.
- Amazon's DeepAR is a global model trained on many related series. Chronos and other foundation models take this idea to the extreme.
- Top solutions of the M5 competition used global gradient boosting models over all Walmart series with lags and calendar features.

## Key points
- Local: one model per series. Global: one model trained on all series together.
- Global models need per-series scaling and benefit from id and static features.
- They help most for many related, short or new series.
- Use the same backtest cutoffs for all series and compare against local baselines.
- Hybrids (groups, clusters) are common in practice.
