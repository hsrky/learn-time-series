---
slug: smape-zero-median
title: SMAPE with Zero Handling and the Median Baseline
difficulty: Medium
type: function
tags: [kaggle, web-traffic, SMAPE, median, missing-data]
skills: [metrics, baseline-first]
packages: []
companies_style: [Kaggle Web Traffic Time Series Forecasting]
---
In the Kaggle *Web Traffic Time Series Forecasting* competition you forecast page views for about 145,000 Wikipedia pages. The metric is **SMAPE** (symmetric mean absolute percentage error). Pages often have zero views and missing days, so the details matter.

**1. `smape(y_true, y_pred)`**

For each day: `200 × |pred − actual| / (|actual| + |pred|)`. Rules:

- If `actual` is `NaN` (missing), ignore that day.
- If `actual` and `pred` are both `0`, the error of that day is `0` (not `NaN`).
- Return the mean over the counted days. If no day is counted, return `0.0`.

(Notice: if the actual is 0 and the prediction is above 0, the error is always 200, the maximum.)

**2. `median_forecast(history, horizon, window)`**

A famous strong baseline: predict the **median of the last `window` days** of the history for every future day. Ignore `NaN` values inside the window. If all values in the window are `NaN`, use `0.0`. Return a numpy array of length `horizon`.

### Example 1
`smape([100, 0, 50], [110, 0, 50])`: day 1: `200 × 10 / 210 = 9.5238`; day 2: 0; day 3: 0. Mean = `3.1746...`.

### Example 2
`median_forecast([5, np.nan, 7, 9], 3, 3)` uses `[nan, 7, 9]` → median 8, so the result is `[8.0, 8.0, 8.0]`.

### Constraints
- 0 ≤ length ≤ 10^5
- `y_pred` ≥ 0 and has no NaN

### Hints
1. Compute numerator `|p − y|` and denominator `|y| + |p|` as arrays.
2. Use `np.where(denominator == 0, 0, ...)` to protect the 0/0 case, then a mask for NaN actuals.
3. For the median use `np.nanmedian` on the last `window` values; handle the all-NaN case yourself.

### Solution explanation
SMAPE is bounded between 0 and 200. The 0/0 rule matters because many pages have zero traffic. Missing actuals are removed from the average. The median baseline is robust to spikes (a viral day) and ignores missing days, which is why it was hard to beat in the competition. Time O(n). Common bugs: dividing 0 by 0 (gives NaN and poisons the mean), counting NaN actuals as zeros, and using the mean instead of the median.
