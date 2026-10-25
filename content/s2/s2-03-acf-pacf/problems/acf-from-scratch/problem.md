---
slug: acf-from-scratch
title: Autocorrelation Function from Scratch
difficulty: Medium
type: function
tags: [acf, autocorrelation, numpy]
skills: [from-scratch]
packages: []
companies_style: [forecasting take-home]
---
Implement the sample [[ACF]] with numpy only. Do not use statsmodels.

Write `acf(x, nlags)`. It returns an array of length `nlags + 1`. Entry `k` is

`r(k) = sum over t = k..n-1 of (x[t] - m) * (x[t-k] - m)  /  sum over all t of (x[t] - m)^2`

where `m` is the mean of `x`. So `r(0) = 1`.

If all values of `x` are equal (zero variance), return `[1, 0, 0, ...]`.

### Example 1
**Input:** `acf([1, 3, 2, 4, 3], 2)`
**Output:** `[1.0, -0.2231, 0.2462]` (rounded)
**Explanation:** The mean is 2.6 and the sum of squared deviations is 5.2. For lag 1 the sum of products is -1.16, and -1.16 / 5.2 = -0.2231.

### Example 2
**Input:** `acf([1, 2, 3, 4, 5, 6], 3)`
**Output:** `[1.0, 0.5, 0.0571, -0.2714]` (rounded; a trend gives steadily falling values)

### Constraints
- `2 <= len(x) <= 10^5`, `0 <= nlags < len(x)`
- Divide **always** by the full sum of squares (this is the standard "biased" estimator, the same as `statsmodels`).
- Avoid a Python loop over the data points. A loop over lags is fine.

### Hints
1. Subtract the mean once: `d = x - x.mean()`.
2. For lag k, the products are `d[k:] * d[:n-k]` (for k = 0 use the whole array).
3. Divide each sum by `np.sum(d * d)`. Handle the zero-variance case first.

### Solution explanation
Centre the data and compute the denominator once. For each lag, slice the array twice (shifted by k) and multiply. This is O(n * nlags) time and O(n) space. An FFT can make it O(n log n), but the loop is clear and fast enough. Common bugs: dividing by `n - k` (a different estimator that does not match), forgetting to centre, and using `d[k:] * d[:-k]` which gives an empty slice for k = 0.
