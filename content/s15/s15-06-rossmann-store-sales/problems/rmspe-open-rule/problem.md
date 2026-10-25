---
slug: rmspe-open-rule
title: RMSPE Ignoring Zero Sales and the Closed-Store Rule
difficulty: Easy
type: function
tags: [kaggle, rossmann, RMSPE, metrics, rules]
skills: [metrics, pandas-fluency]
packages: []
companies_style: [Kaggle Rossmann Store Sales]
---
In *Rossmann Store Sales* the metric is **RMSPE** (root mean squared percentage error):

`RMSPE = sqrt( mean( ((y − p) / y)² ) )`

Days with `y = 0` (the store was closed) are **ignored** in the score, because the percentage is undefined. A good solution also uses a simple rule: if the store is closed (`Open == 0`) the sales prediction is exactly 0.

Write two functions.

**1. `rmspe(y_true, y_pred)`** — compute the RMSPE only over the rows where `y_true != 0`. If no such row exists, return `0.0`.

**2. `apply_open_rule(df)`** — `df` has columns `Open` (1, 0 or NaN) and `pred`. Return a Series (same index as `df`) with `0.0` where `Open == 0` and `pred` otherwise. A missing `Open` (NaN) is treated as **open**.

### Example 1
`rmspe([100, 0, 200], [110, 5, 180])` ignores the middle row: errors are `0.1` and `0.1`, so the result is `0.1`.

### Example 2
`Open = [1, 0, NaN]`, `pred = [50, 40, 30]` gives `[50.0, 0.0, 30.0]`.

### Constraints
- 0 ≤ length ≤ 10^5, `y_true` ≥ 0

### Hints
1. Make a boolean mask `y_true != 0`.
2. Compute the percentage error only on the masked rows, square, mean, square root.
3. For the rule, use `Series.where(df["Open"] != 0, 0.0)`. NaN is not equal to 0, so it stays open.

### Solution explanation
RMSPE punishes errors relative to the size of the actual value, so small days weigh as much as big days. Ignoring zeros avoids division by zero and matches the competition scoring. The open rule removes a whole class of errors for free: a model should never predict sales for a closed store. Time O(n). Common bugs: dividing by the prediction instead of the actual, forgetting the mask, and treating NaN `Open` as closed.
