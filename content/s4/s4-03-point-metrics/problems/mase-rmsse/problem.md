---
slug: mase-rmsse
title: MASE and RMSSE
difficulty: Medium
type: function
tags: [metrics, mase, rmsse, scaling]
skills: [metrics, from-scratch, baseline-first]
packages: []
---
Write two functions that compare a forecast with a naive method measured on the **training** data.

`mase(y_true, y_pred, y_train, m=1)`

- `scale` = mean of `|y_train[t] − y_train[t−m]|` for all `t ≥ m` (the in-sample seasonal naive error with period `m`).
- Return `mean(|y_true − y_pred|) / scale`.

`rmsse(y_true, y_pred, y_train, m=1)`

- `scale2` = mean of `(y_train[t] − y_train[t−m])²` for all `t ≥ m`.
- Return `sqrt(mean((y_true − y_pred)²) / scale2)`.

Edge cases for both: if `y_train` has `m` or fewer values, or the scale is 0, return `nan`.

### Example 1
**Input:** `y_true=[10, 20, 30, 40]`, `y_pred=[12, 18, 33, 36]`, `y_train=[10, 12, 11, 13, 15, 14, 16, 18]`, `m=1`

**Output:** `mase = 1.604`, `rmsse = 1.62`

**Explanation:** MAE = 2.75. The naive scale is the mean of the seven absolute differences = 12/7 = 1.714. 2.75 / 1.714 = 1.604.

### Example 2
**Input:** `y_train=[1, 5, 2, 6, 3, 7]`, `m=2`, test `y_true=[4]`, `y_pred=[6]`

**Output:** `mase = 2/1.0 = 2.0`

**Explanation:** With m = 2 the differences are 2−1, 6−5, 3−2, 7−6 = 1, 1, 1, 1. The scale is 1. The MAE is 2.

### Constraints
- 0 ≤ length of each array ≤ 10^5. `m ≥ 1`.

### Hints
1. With `numpy`, the lag-`m` differences are `y_train[m:] - y_train[:-m]`.
2. Check `len(y_train) <= m` before you compute them.
3. Return `float("nan")` when the scale is 0 (a flat training series).

### Solution explanation
Build the lag-`m` difference array, take the mean of its absolute (or squared) values as the scale, and divide the test error by it. Time O(n). The scale must come from the training data. A bug is using `np.diff` when `m > 1`: `np.diff` always uses lag 1.
