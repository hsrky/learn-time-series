---
slug: random-walk-forecast-interval
title: Random Walk Forecast with Interval
difficulty: Easy
type: function
tags: [random-walk, prediction-interval, baseline]
skills: [baseline-first, uncertainty]
packages: []
companies_style: [finance, demand planning]
---
A [[random walk]] with drift has this rule: each new value is the last value, plus a constant `drift`, plus a random shock.

Write `random_walk_forecast(last, h, sigma, drift=0.0, z=1.96)`.

- `last`: the last observed value.
- `h`: how many steps ahead to forecast (an integer, `h >= 1`).
- `sigma`: the standard deviation of one shock.
- `drift`: the constant push per step.
- `z`: the z-value for the interval (1.96 gives about 95%).

Return a dict with three lists of length `h`:

- `"forecast"`: for step k = 1..h, `last + k * drift`.
- `"lower"` and `"upper"`: forecast minus and plus `z * sigma * sqrt(k)`.

### Example 1
**Input:** `random_walk_forecast(100, 3, 2.0)`
**Output:** `{"forecast": [100.0, 100.0, 100.0], "lower": [96.08, 94.456..., 93.210...], "upper": [103.92, 105.543..., 106.789...]}`
**Explanation:** The forecast is flat at 100. The half-width at k = 1 is 1.96 * 2 * 1 = 3.92. It grows with the square root of k.

### Example 2
**Input:** `random_walk_forecast(10, 2, 1.0, drift=0.5)`
**Output:** forecast `[10.5, 11.0]`, lower `[8.54, 8.228...]`, upper `[12.46, 13.771...]`.

### Constraints
- `1 <= h <= 1000`
- `sigma >= 0`
- Return plain Python lists of floats.

### Hints
1. Make an array `k = 1, 2, ..., h` with `np.arange(1, h + 1)`.
2. The forecast is `last + drift * k`. The half-width is `z * sigma * np.sqrt(k)`.
3. Build `lower` and `upper` from the forecast and the half-width. Use `.tolist()` at the end.

### Solution explanation
A shock is added at each step. After k steps the errors add up. Independent errors add their variances, so the variance is `k * sigma^2` and the standard deviation is `sigma * sqrt(k)`.

1. Build `k`.
2. Compute the forecast and the half-width with numpy.
3. Return the three lists.

Time and space: O(h). Common bug: using `k` instead of `sqrt(k)` for the width, or starting `k` at 0.
