---
slug: piecewise-linear-trend
title: Piecewise Linear Trend with Changepoints
difficulty: Medium
type: function
tags: [prophet, trend, changepoints, least-squares, numpy]
skills: [from-scratch-algorithms, numpy-fluency]
packages: []
companies_style: [forecasting library, trend modelling]
---
Prophet models a trend as a line whose **slope can change** at chosen points called **changepoints**. You will fit this idea with ordinary least squares.

Let `t = 0, 1, …, n−1` be the time index of the series `y`. For a list of changepoints `c_1, …, c_k` (integers), build the model

`trend(t) = a + b·t + d_1·max(0, t − c_1) + … + d_k·max(0, t − c_k)`

Each `d_j` is the **change of slope** at `c_j`. Fit `a, b, d_1 … d_k` with least squares on `y` (use `np.linalg.lstsq`).

Write `piecewise_trend(y, changepoints, horizon=0)`. Return a numpy array of the fitted trend for `t = 0 … n−1+horizon`. When `horizon > 0`, the extra values continue the **last** line (this is how the trend is extrapolated into the future).

### Example 1
**Input:** `y = [0, 1, 2, 3, 4, 3, 2, 1]`, `changepoints = [4]`, `horizon = 2`
**Output:** `[0, 1, 2, 3, 4, 3, 2, 1, 0, -1]`
**Explanation:** The slope is +1 until t = 4 and −1 after. The data lie exactly on this shape, so the fit is perfect, and the last line goes on with slope −1.

### Constraints
- 2 ≤ n ≤ 10 000. 0 ≤ k ≤ 50. Each changepoint satisfies 0 < c < n−1. Changepoints are distinct.
- `horizon ≥ 0`.

### Hints
1. Build a design matrix with columns `1`, `t`, and one column `np.maximum(0, t - c)` per changepoint.
2. `np.linalg.lstsq(X, y, rcond=None)[0]` returns the coefficients.
3. To extrapolate, build the same matrix for `t = 0 … n−1+horizon` and multiply by the coefficients.

### Solution explanation
The hinge columns `max(0, t − c)` are zero before the changepoint and grow with slope 1 after it, so their coefficients are slope changes. Least squares finds the best coefficients in O(n·k²). Prophet itself uses many changepoints with a penalty (a Laplace prior) that keeps most slope changes near zero; plain least squares has no penalty, so with many changepoints it will overfit. Common bugs: using `t − c` without the `max`, forgetting the intercept, and starting `t` at 1 (the answer is still the same fit, but the example indexes start at 0).
