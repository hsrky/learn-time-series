---
slug: rmsle-seasonal-naive-submission
title: RMSLE and a Seasonal Naive Submission
difficulty: Medium
type: function
tags: [kaggle, RMSLE, seasonal-naive, store-sales, pandas]
skills: [metrics, baseline-first, pandas-fluency]
packages: []
companies_style: [Kaggle Store Sales, retail demand]
---
In the Kaggle competition *Store Sales – Time Series Forecasting* every row is a **store × product family × day**. The metric is **RMSLE** (root mean squared logarithmic error). In this mini version you write the metric and the first baseline.

**1. `rmsle(y_true, y_pred)`**

`RMSLE = sqrt( mean( (log(1 + pred) − log(1 + true))² ) )`

Negative predictions must be clipped to 0 first. Return a float.

**2. `seasonal_naive_forecast(train, test_dates, season=7)`**

`train` is a DataFrame with columns `store_nbr`, `family`, `date` (datetime), `sales`. For each (`store_nbr`, `family`) series in `train` and each date `d` in `test_dates`, forecast the value of the same position in the **last `season` days** of the training data. Let `last` be the latest date in `train` (over all series). The source date is

`d − season × ceil((d − last).days / season)`

If the source date has no row for that series, use `0.0`.

Return a DataFrame with columns `store_nbr, family, date, sales`, sorted by `store_nbr`, `family`, `date`, with index `0, 1, 2, ...`.

### Example 1
`rmsle([3, 0], [3, 0])` returns `0.0`. `rmsle([0], [3])` returns `log(4) = 1.3862943611198906`.

### Example 2
Train has one series with daily sales on `2024-01-01 ... 2024-01-14` equal to `1, 2, ..., 14`. Then `last = 2024-01-14`. For `test_dates = [2024-01-15, 2024-01-22]` and `season = 7`:
- `2024-01-15`: `ceil(1/7) = 1`, source `2024-01-08`, forecast `8.0`.
- `2024-01-22`: `ceil(8/7) = 2`, source `2024-01-08`, forecast `8.0`.

### Constraints
- 1 ≤ number of series ≤ 2,000; training history ≤ 2,000 days
- `test_dates` are all after `last`
- `sales` ≥ 0

### Hints
1. For RMSLE use `np.log1p` on both arrays and `np.clip(pred, 0, None)`.
2. Build all (series, date) pairs with `merge(..., how="cross")`, compute the source date with `np.ceil`, then merge the training sales on (`store_nbr`, `family`, source date).
3. Fill missing values with `0.0` and sort.

### Solution explanation
RMSLE compares sales on a log scale, so a 10-unit error on a small store matters as much as a 1000-unit error on a big store in relative terms. `log1p` also handles zero sales. The seasonal naive forecast uses the last full week for every series, which keeps the weekday pattern. The merge approach is vectorised: O(series × days) time. Common bugs: using `np.log` (fails at 0), forgetting to clip negative predictions, and taking the source date from the wrong week when the test period is longer than one season.
