---
slug: recursive-forecast-lstsq
title: Recursive AR Forecast with Least Squares
difficulty: Medium
type: function
tags: [numpy, lstsq, recursive, autoregression]
skills: [from-scratch]
packages: []
---
Write `recursive_forecast(y, p, h)`.

1. Build the training table from **all** windows of `y`: features are `p` consecutive values `y[i], …, y[i+p-1]` plus a constant `1` (intercept), and the target is the next value `y[i+p]`.
2. Fit the weights `w` with `np.linalg.lstsq(A, target, rcond=None)`.
3. Forecast `h` steps **recursively**: predict the next value from the last `p` values, append the prediction to the history, and repeat.

Return a `numpy` array of length `h`. Assume `len(y) > p` and `h ≥ 1`.

### Example 1
**Input:** `y = [1, 2, 3, 4, 5, 6]`, `p = 2`, `h = 3`

**Output:** `[7, 8, 9]`

**Explanation:** The series is a straight line, so `y[t] = 2·y[t−1] − y[t−2]` fits exactly (also with the intercept). The recursion continues the line.

### Example 2
**Input:** `y = [5, 5, 5, 5]`, `p = 1`, `h = 2`

**Output:** `[5, 5]`

**Explanation:** A constant series is predicted as a constant.

### Constraints
- 2 ≤ len(`y`) ≤ 10^4, 1 ≤ `p` < len(`y`), 1 ≤ `h` ≤ 100.

### Hints
1. The table has `len(y) - p` rows. `np.array([y[i:i+p] for i in range(n)])` works; `sliding_window_view` is faster.
2. Add the intercept column with `np.c_[X, np.ones(n)]`.
3. In the loop, take `history[-p:]`, append `1.0`, multiply with `w`, and append the result to `history`.

### Solution explanation
Least squares finds the weights that minimize the squared one-step error. The loop feeds each prediction back, so step `k` depends on steps `1 … k−1` (error feedback). Time O(n·p²) for the fit plus O(h·p). Common bugs: using true values instead of predictions as lags, and forgetting the intercept column.
