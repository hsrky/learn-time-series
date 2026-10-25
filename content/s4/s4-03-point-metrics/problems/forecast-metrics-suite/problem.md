---
slug: forecast-metrics-suite
title: Forecast Metrics Suite
difficulty: Medium
type: function
tags: [metrics, mae, rmse, mape, smape, wape]
skills: [metrics, from-scratch]
packages: []
---
Write `point_metrics(y_true, y_pred)` that returns a dictionary with five keys: `"mae"`, `"rmse"`, `"mape"`, `"smape"`, `"wape"`.

Both inputs are equal-length lists or arrays of numbers. Definitions (percent values are in **percent**, for example 12.5, not 0.125):

- `mae` = mean of `|y − ŷ|`.
- `rmse` = square root of the mean of `(y − ŷ)²`.
- `mape` = mean of `|y − ŷ| / |y|` × 100, **using only the points where `y != 0`**. If every `y` is 0, return `nan`.
- `smape` = mean of `2·|y − ŷ| / (|y| + |ŷ|)` × 100. A point where `|y| + |ŷ| = 0` counts as an error of 0 (it is a perfect forecast).
- `wape` = sum of `|y − ŷ|` divided by sum of `|y|`. If the sum of `|y|` is 0, return `nan`.

If the inputs are empty, all five values are `nan`.

### Example 1
**Input:** `y_true=[10, 20, 30, 40]`, `y_pred=[12, 18, 33, 36]`

**Output:** `{"mae": 2.75, "rmse": 2.872, "mape": 12.5, "smape": 12.19, "wape": 0.11}` (rounded here)

**Explanation:** Errors are 2, 2, 3, 4. MAPE = mean(0.2, 0.1, 0.1, 0.1) × 100 = 12.5.

### Example 2
**Input:** `y_true=[0, 10]`, `y_pred=[3, 12]`

**Output:** `mae=2.5`, `mape=20.0`

**Explanation:** The first point has `y = 0` and is skipped for MAPE. The second gives 2/10 = 20%.

### Constraints
- 0 ≤ length ≤ 10^5. Values are finite floats.

### Hints
1. Convert the inputs to float `numpy` arrays and compute `e = y − ŷ`.
2. For MAPE use a boolean mask `y != 0`. For sMAPE compute the denominator first and mask where it is 0.
3. Check for empty input and zero sums at the start, before dividing.

### Solution explanation
Vectorized numpy: one pass for each metric, with masks for the special cases. Time O(n). The traps: dividing by zero (MAPE, sMAPE, WAPE), and returning a fraction when percent is asked.
