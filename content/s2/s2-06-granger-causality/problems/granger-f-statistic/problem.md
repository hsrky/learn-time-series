---
slug: granger-f-statistic
title: Granger F-Statistic from Scratch
difficulty: Medium
type: function
tags: [granger, regression, f-test, numpy]
skills: [from-scratch]
packages: []
companies_style: [marketing analytics]
---
Implement the F statistic of a Granger test with numpy only (`np.linalg.lstsq` is allowed).

Write `granger_f(y, x, p)`. It tests if the past of `x` helps to predict `y`.

For the rows `t = p, p+1, ..., n-1` fit two regressions with a constant term:

- **Restricted:** `y[t]` on `y[t-1], ..., y[t-p]`
- **Unrestricted:** `y[t]` on `y[t-1], ..., y[t-p]` and `x[t-1], ..., x[t-p]`

Let `RSS_r` and `RSS_u` be the sums of squared residuals. Return

`F = ((RSS_r - RSS_u) / p) / (RSS_u / df2)` with `df2 = (n - p) - (2 * p + 1)`.

Also write `granger_direction(x, y, p, crit)`. It computes `f_xy = granger_f(y, x, p)` ("x causes y") and `f_yx = granger_f(x, y, p)`. Return:

- `"x->y"` if only `f_xy > crit`
- `"y->x"` if only `f_yx > crit`
- `"both"` if both are above `crit`
- `"none"` if neither is

### Example 1
**Input:** `y = [0,1,0,2,1,3,2,4,3,5]`, `x = [1,0,2,1,3,2,4,3,5,4]`, `p = 1`
**Output:** about 0.6 or so; the exact float follows from the formula (here df2 = 9 - 3 = 6).

### Example 2
**Input:** an `x` of random noise, and `y(t) = 0.3 y(t-1) + 0.8 x(t-1) + noise`, `p = 2`
**Output:** `granger_f(y, x, 2)` is large (about 473). `granger_f(x, y, 2)` is small (about 0.1).

### Constraints
- `n - p > 2 * p + 1` so `df2 > 0`
- `1 <= p <= 10`
- Assume `RSS_u > 0`.

### Hints
1. Build the lag columns with slices: `y[p-k : n-k]` is `y(t-k)` for `t = p..n-1`.
2. `np.column_stack` builds the design matrix. Add a column of ones for the constant.
3. A helper `rss(X)` that solves `lstsq` and returns `residual @ residual` keeps the code short.

### Solution explanation
The restricted model has `p + 1` parameters, the unrestricted one `2p + 1`. The F-test compares the drop in error per added parameter with the remaining error per degree of freedom. If the lags of x carry information, the drop is large and F is large. Time is O(n * p^2) for the least squares. Common bugs: wrong lag slices (an off-by-one gives look-ahead!), forgetting the constant, and a wrong `df2`.
