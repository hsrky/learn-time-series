---
slug: ljung-box-q
title: Ljung-Box Statistic from Scratch
difficulty: Medium
type: function
tags: [ljung-box, residuals, acf, diagnostics]
skills: [from-scratch, backtest]
packages: []
companies_style: [forecasting interview]
---
After you fit a model, you test if the [[residual]]s are white noise. The Ljung-Box statistic does this with one number.

Write `ljung_box(resid, nlags, n_params=0)`.

1. Compute the sample autocorrelation `r(k)` of the residuals for `k = 1..nlags`. Use the standard estimator: centre the data, divide each lag sum by the sum of squares of all centred values.
2. `Q = n * (n + 2) * sum over k=1..nlags of r(k)^2 / (n - k)`, where `n = len(resid)`.
3. Degrees of freedom: `df = nlags - n_params`, where `n_params` is the number of fitted ARMA parameters (p + q).

Return a dict `{"q": Q, "df": df}`.

A large `Q` (compared with a chi-square value for `df`) means the residuals are not white noise. You do not need the p-value here.

### Example 1
**Input:** `ljung_box([1, -1, 1, -1, 1, -1, 1, -1], 2)`
**Output:** `{"q": 16.25, "df": 2}`
**Explanation:** n = 8, r(1) = -0.875 and r(2) = 0.75. Q = 8 * 10 * (0.7656 / 7 + 0.5625 / 6) = 16.25.

### Example 2
**Input:** `ljung_box(noise, 10, n_params=2)` for 500 white-noise values
**Output:** `Q` is a small number, typically near 8 (the mean of a chi-square with 8 degrees of freedom), and `df = 8`.

### Constraints
- `1 <= nlags < len(resid)`, `0 <= n_params < nlags`
- Constant residuals (zero variance): return `{"q": 0.0, "df": nlags - n_params}`.

### Hints
1. Centre the data: `d = x - x.mean()`. The denominator is `d @ d`.
2. For each lag, `r_k = (d[k:] * d[:n-k]).sum() / denom`.
3. Vectorise the final sum with `np.arange(1, nlags + 1)`.

### Solution explanation
The Ljung-Box statistic adds the squared autocorrelations, with weights `n(n+2)/(n-k)` that give a better small-sample behaviour than the older Box-Pierce statistic. Under H0 (white noise) Q follows a chi-square distribution with `df` degrees of freedom. Time O(n * nlags). Common bugs: using `n - k` incorrectly in the weights, dividing by `n - k` in the autocorrelation (use the full sum of squares), and forgetting to subtract `n_params` from the degrees of freedom.
