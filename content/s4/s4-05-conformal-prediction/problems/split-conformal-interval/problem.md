---
slug: split-conformal-interval
title: Split Conformal Intervals
difficulty: Medium
type: function
tags: [conformal, intervals, uncertainty]
skills: [uncertainty, from-scratch]
packages: []
---
You have a trained forecaster. On a calibration set you computed the **absolute residuals** `|y − ŷ|`. Write `split_conformal(cal_residuals, y_pred, alpha)`.

- Let `n` be the number of calibration residuals.
- Let `k = ceil((n + 1) * (1 - alpha))`.
- The half-width `q` is the `k`-th smallest residual (`k` counts from 1). If `k > n`, then `q = inf`.
- Return two `numpy` arrays `(lower, upper)` with `lower = y_pred - q` and `upper = y_pred + q`.
- If `n == 0`, return arrays of `nan` with the same length as `y_pred`.

Careful with floating-point: compute `k` with `math.ceil` after rounding the product to 9 decimals: `math.ceil(round((n + 1) * (1 - alpha), 9))`.

### Example 1
**Input:** `cal_residuals=[1, 2, 2, 3, 3, 4, 5, 6, 9]`, `y_pred=[100, 50]`, `alpha=0.2`

**Output:** `lower=[94, 44]`, `upper=[106, 56]`

**Explanation:** `n = 9`, `k = ceil(10 × 0.8) = 8`. The 8th smallest residual is 6.

### Example 2
**Input:** `cal_residuals=[1, 2, 3]`, `y_pred=[10]`, `alpha=0.1`

**Output:** `lower=[-inf]`, `upper=[inf]`

**Explanation:** `k = ceil(4 × 0.9) = 4 > 3`. There are too few residuals for a 90% interval.

### Constraints
- 0 ≤ n ≤ 10^5. `0 < alpha < 1`. The residuals are not sorted.

### Hints
1. Sort the residuals first.
2. Compute `k`, then check `k <= n`.
3. Index with `k - 1`, because Python counts from 0.

### Solution explanation
After sorting, the `k`-th smallest value is `sorted[k-1]`. The `+1` in `n + 1` is the finite-sample correction that gives the guarantee `P(y in interval) >= 1 − alpha` when calibration and test points are exchangeable. Time O(n log n). Common bugs: using `np.quantile` (it interpolates and has no `n+1` correction), and off-by-one in the index.
