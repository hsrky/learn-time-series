---
slug: ets-forecast-beats-naive
title: Holt-Winters Forecast That Beats Seasonal Naive
difficulty: Medium
type: forecast
tags: [statsmodels, ets, holt-winters, forecast]
skills: [exponential-smoothing, statsmodels]
packages: [statsmodels]
companies_style: [retail demand, energy load]
---
Write `ets_forecast(train, h, m)` that forecasts the next `h` values of `train` with an **additive-trend, additive-seasonal Holt-Winters** model from statsmodels, with season length `m`.

Use `statsmodels.tsa.holtwinters.ExponentialSmoothing(train, trend="add", seasonal="add", seasonal_periods=m)`, call `.fit()`, then `.forecast(h)`. Return a numpy array of length `h`.

The judge compares your forecast with hidden future values. You pass a case when your MAE is **at most 80%** of the MAE of the seasonal naive forecast (repeat the last season).

### Example 1
**Input:** `train` = 10 weeks of daily data with an upward trend and a weekly season, `h = 14`, `m = 7`
**Output:** an array of 14 numbers that follows the trend and the weekly pattern.
**Explanation:** Seasonal naive repeats the last week and misses the trend, so a model with a trend term does better.

### Constraints
- `len(train) ≥ 2·m`. `1 ≤ h ≤ 3·m`. `2 ≤ m ≤ 24`.
- `train` is a 1-D array of positive floats.

### Hints
1. Import `ExponentialSmoothing` from `statsmodels.tsa.holtwinters`.
2. Pass `trend="add"`, `seasonal="add"` and `seasonal_periods=m`.
3. `model.fit().forecast(h)` returns the forecast. Convert it with `np.asarray`.

### Solution explanation
Holt-Winters keeps three smoothed states: level, trend and season. The additive version adds the trend and the seasonal term to the level. A seasonal naive forecast repeats the last season, so it ignores the trend and keeps the noise of the last season. The fitted model averages over the whole history, so it usually has a lower error when the data have a trend and a stable season. Complexity: the optimiser runs a few hundred iterations over `n` points. Common bugs: forgetting `seasonal_periods`, using multiplicative terms on data with zeros, and returning a Series with an index instead of an array of length `h`.
