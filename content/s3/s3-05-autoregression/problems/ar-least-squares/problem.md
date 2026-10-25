---
slug: ar-least-squares
title: Fit AR(p) with Least Squares
difficulty: Medium
type: function
tags: [ar, least-squares, numpy, from-scratch]
skills: [from-scratch]
packages: []
companies_style: [forecasting take-home]
---
Fit an autoregressive model of order `p` with numpy. Do not use statsmodels or scikit-learn.

The model is `y[t] = c + phi1*y[t-1] + ... + phip*y[t-p] + error`.

Write `fit_ar(y, p)`. Build the regression table with one row for each `t = p, ..., n-1` (0-based). Each row has a `1` for the constant, then `y[t-1], y[t-2], ..., y[t-p]` in that order. The target is `y[t]`. Solve it by least squares.

Return a numpy array `[c, phi1, ..., phip]` of length `p + 1`.

### Example 1
**Input:** `fit_ar([1, 2, 3, 4, 5, 6], 1)`
**Output:** `array([1., 1.])`
**Explanation:** Each value is the previous one plus 1: `y[t] = 1 + 1 * y[t-1]`.

### Example 2
**Input:** a series from `y[t] = 2 + 0.5 y[t-1] + 0.3 y[t-2] + noise` with 2000 points, `p = 2`
**Output:** close to `[2, 0.5, 0.3]` (for example `[2.08, 0.51, 0.28]`).

### Constraints
- `p >= 1`, `len(y) >= 2 * p + 2`
- Use `np.linalg.lstsq`.
- The column order of the lags matters: `phi1` belongs to the **most recent** lag.

### Hints
1. The target is `y[p:]`.
2. The lag-k column is `y[p-k : n-k]`.
3. Stack `[ones, lag1, lag2, ..., lagp]` with `np.column_stack` and call `lstsq`.

### Solution explanation
The AR model is linear in its parameters, so least squares gives the best coefficients. The slice `y[p-k : n-k]` lines up each target `y[t]` with its k-th lag. Time O(n * p^2). The solution loses `p` rows. Common bugs: wrong lag order (reversed coefficients), no constant column, and using a slice that does not line up with the target (off by one).
