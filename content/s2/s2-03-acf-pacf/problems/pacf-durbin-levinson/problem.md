---
slug: pacf-durbin-levinson
title: PACF with Durbin-Levinson
difficulty: Hard
type: function
tags: [pacf, acf, yule-walker, numpy]
skills: [from-scratch]
packages: []
companies_style: [forecasting take-home]
---
The [[PACF]] at lag k is the last coefficient `phi(k,k)` of an AR(k) model fitted to the series. You can compute all of them from the [[ACF]] with the **Durbin-Levinson** recursion. No regression is needed.

Write `pacf(x, nlags)`. It returns an array of length `nlags + 1`. Entry 0 is `1.0`.

Let `r[0..nlags]` be the sample ACF (centre `x`, divide each lag sum by the full sum of squares).

- `phi(1,1) = r[1]`
- For k >= 2:
  `phi(k,k) = ( r[k] - sum_{j=1}^{k-1} phi(k-1,j) * r[k-j] ) / ( 1 - sum_{j=1}^{k-1} phi(k-1,j) * r[j] )`
- For j = 1..k-1: `phi(k,j) = phi(k-1,j) - phi(k,k) * phi(k-1,k-j)`

The output is `[1, phi(1,1), phi(2,2), ..., phi(nlags,nlags)]`.

If `x` is constant, return `[1, 0, 0, ...]`.

### Example 1
**Input:** `pacf([1, 3, 2, 4, 3, 5, 4, 6], 2)`
**Output:** an array of length 3 starting with `1.0`. Entry 1 equals the lag-1 autocorrelation of the data.
**Explanation:** The first partial autocorrelation always equals the first autocorrelation.

### Example 2
**Input:** a long AR(1) series with phi = 0.7 and `nlags = 3`
**Output:** about `[1, 0.7, 0, 0]`. The PACF cuts off after lag 1.

### Constraints
- `3 <= len(x) <= 10^4`, `1 <= nlags < len(x)`
- Results must match `statsmodels.tsa.stattools.pacf(x, nlags, method="ywm")` within 1e-8.

### Hints
1. First write a small `acf` helper, with the standard biased estimator.
2. Keep an array `phi` with the AR coefficients of the current order. Start with `phi = [r[1]]`.
3. At each new k, compute the new `phi(k,k)` with the two dot products. Then update the old coefficients with `phi - phi_kk * phi[::-1]` and append `phi_kk`.

### Solution explanation
Durbin-Levinson solves the Yule-Walker equations one order at a time. Moving from order k-1 to order k reuses the old coefficients, so each step costs O(k). Total time is O(nlags^2) plus the ACF cost, and space is O(nlags). Common bugs: wrong index order in `r[1:k][::-1]`, forgetting to update all old coefficients before appending the new one, and not handling a zero denominator for constant series.
