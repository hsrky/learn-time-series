---
slug: baseline-forecasts
title: Four Baseline Forecasts
difficulty: Easy
type: function
tags: [baseline, naive, seasonal-naive, drift]
skills: [baseline-first, from-scratch]
packages: []
companies_style: [retail demand, energy load]
---
Implement the four classic [[baseline]] forecasts with numpy.

Write `baseline_forecast(y, h, method, m=1)`. It returns a numpy array with `h` forecasts for the steps `n+1, ..., n+h`, where `n = len(y)`.

- `"mean"`: every forecast is the mean of `y`.
- `"naive"`: every forecast is the last value `y[-1]`.
- `"seasonal_naive"`: the forecast for step `n+j` is the value one season earlier, repeated if needed. For `j = 1..h` use `y[n - m + (j - 1) % m]`.
- `"drift"`: `y[-1] + j * (y[-1] - y[0]) / (n - 1)`. If `n == 1` the slope is 0.

Raise `ValueError` for an unknown method, or if `method == "seasonal_naive"` and `len(y) < m`.

### Example 1
**Input:** `baseline_forecast([10, 12, 14, 13], 3, "drift")`
**Output:** `[14.0, 15.0, 16.0]`
**Explanation:** The slope is (13 - 10) / 3 = 1.

### Example 2
**Input:** `baseline_forecast([10, 20, 30, 40, 12, 22, 32, 42], 6, "seasonal_naive", m=4)`
**Output:** `[12, 22, 32, 42, 12, 22]`
**Explanation:** Copy the last season again and again.

### Constraints
- `1 <= len(y) <= 10^5`, `1 <= h <= 1000`, `1 <= m <= len(y)` for seasonal naive.
- Return floats in a numpy array.

### Hints
1. Convert `y` with `np.asarray(y, dtype=float)` and build `j = np.arange(1, h + 1)`.
2. For seasonal naive, use integer-array indexing: `y[n - m + (j - 1) % m]`.
3. For drift, compute the slope once: `(y[-1] - y[0]) / (n - 1)`. Care for `n == 1`.

### Solution explanation
All four methods are one-liners with vectorized numpy. The seasonal index `(j - 1) % m` cycles through the last season, so forecasts beyond one season repeat it. Time O(n + h) (the mean is O(n)). Common bugs: using `y[-m:]` and a wrong cycle start, dividing by `n` instead of `n - 1` in the drift slope, and using the mean of the last season instead of its values.
