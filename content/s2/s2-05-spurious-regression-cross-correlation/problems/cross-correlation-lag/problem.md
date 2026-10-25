---
slug: cross-correlation-lag
title: Find the Lead-Lag Between Two Series
difficulty: Medium
type: function
tags: [cross-correlation, lead-lag, numpy]
skills: [from-scratch]
packages: []
companies_style: [marketing analytics, demand planning]
---
Two series `x` and `y` have the same length `n`. You want to know which one leads, and by how many steps.

Define the cross-correlation at lag `k` as the Pearson correlation between

- for `k >= 0`: `x[0 : n-k]` and `y[k : n]` (x leads y by k steps)
- for `k < 0`: `x[-k : n]` and `y[0 : n+k]` (y leads x by -k steps)

Write `best_lead_lag(x, y, max_lag, difference=True)`:

1. If `difference` is `True`, first replace both series by their first differences (`np.diff`), to avoid [[spurious regression]].
2. Compute the cross-correlation for every lag from `-max_lag` to `+max_lag`.
3. Return a dict `{"lag": k, "corr": r}` where `k` has the largest **absolute** correlation and `r` is that correlation (with its sign), rounded to 4 decimals.
4. If two lags have exactly the same absolute value, choose the one with the smallest `abs(k)`, and then the positive one.
5. If a lag leaves fewer than 3 overlapping points, or one of the two slices has zero variance, skip that lag. (If you skip all lags, return `{"lag": 0, "corr": 0.0}`.)

### Example 1
**Input:** `x = [1, 3, 2, 5, 4, 6]`, `y = [0, 0, 1, 3, 2, 5]`, `max_lag = 2`, `difference=False`
**Output:** `{"lag": 2, "corr": 1.0}`
**Explanation:** `y(t) = x(t-2)` for the last 4 points, so x leads y by 2.

### Example 2
**Input:** the same arrays with `max_lag = 0`
**Output:** `{"lag": 0, "corr": 0.9089}`. With no shift, the plain correlation of the two arrays is 0.9089.

### Constraints
- `3 <= n <= 10^5`, `0 <= max_lag < n - 2`
- Do not call `np.correlate`. Use `np.corrcoef` or write the formula.

### Hints
1. Write a small helper `corr_at(a, b, k)` that slices the two arrays as in the statement.
2. Loop `k` over `range(-max_lag, max_lag + 1)` and keep the best key `(-abs(r), abs(k), -k)` with `min`.
3. Use `np.std(...) == 0` to detect constant slices before calling `corrcoef`.

### Solution explanation
Slicing makes the overlap for each lag. One correlation costs O(n), and there are 2 * max_lag + 1 lags, so the total is O(n * max_lag). Differencing first removes trends, so a common drift does not create a fake peak. Common bugs: swapping the sign convention, forgetting that differencing reduces the length by one, and not handling constant slices (corrcoef would give NaN).
