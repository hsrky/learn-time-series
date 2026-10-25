---
slug: acf-dominant-season
title: Find the Season with the ACF
difficulty: Easy
type: function
tags: [statsmodels, acf, seasonality, period]
skills: [acf-pacf, statsmodels]
packages: [statsmodels]
companies_style: [demand forecasting, traffic]
---
You receive a series with an unknown season length. The **autocorrelation function (ACF)** shows it: the ACF is high at the lag equal to the season length.

Write `dominant_season(y, max_lag)`.

1. Take the **first difference** of `y` with `np.diff`. This removes a trend, which would otherwise hide the season.
2. Compute `statsmodels.tsa.stattools.acf(d, nlags=max_lag, fft=True)`. The result has `max_lag + 1` values; position `k` is the ACF at lag `k`.
3. Among lags `2 … max_lag`, return the lag with the **highest** ACF value (as a Python `int`). If there is a tie, return the smaller lag.

### Example 1
**Input:** `y` with a clear weekly cycle plus noise, `max_lag = 10`
**Output:** `7`

### Example 2
**Input:** `y` with a 12-step cycle and a strong upward trend, `max_lag = 20`
**Output:** `12`

### Constraints
- 30 ≤ length ≤ 5 000. `3 ≤ max_lag < length // 2`.
- Values are finite floats.

### Hints
1. `d = np.diff(y)`.
2. `r = acf(d, nlags=max_lag, fft=True)`. Ignore `r[0]` and `r[1]`.
3. `np.argmax(r[2:]) + 2` gives the lag. `np.argmax` returns the first (smallest) index on ties.

### Solution explanation
A series with season length `m` is similar to itself shifted by `m` steps, so its ACF has a peak at lag `m`. A trend makes the ACF of the raw series decay slowly and hides peaks, so we difference first. Skipping lags 0 and 1 avoids the trivial peak at lag 0 and the common correlation at lag 1. Complexity: O(n log n) with the FFT. Common bugs: forgetting to difference, an off-by-two index after slicing, and looking beyond `max_lag` so that multiples of the period (2m) win.
