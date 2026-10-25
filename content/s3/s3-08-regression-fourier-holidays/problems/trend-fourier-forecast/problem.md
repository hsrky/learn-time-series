---
slug: trend-fourier-forecast
title: Trend + Fourier Regression Forecast
difficulty: Medium
type: function
tags: [regression, fourier, trend, forecast]
skills: [from-scratch, baseline-first]
packages: []
companies_style: [demand forecasting]
---
Fit a regression with a linear trend and Fourier seasonality. Then forecast the next `h` steps. This is a simple version of the Prophet idea.

Write `trend_fourier_forecast(y, period, K, h)`.

1. Let `n = len(y)` and `t = 0, 1, ..., n-1`.
2. Build the feature matrix with the columns `[1, t, sin(2*pi*1*t/period), cos(2*pi*1*t/period), ..., sin(2*pi*K*t/period), cos(2*pi*K*t/period)]`.
3. Fit the weights with `np.linalg.lstsq` on the training rows.
4. Build the same features for `t = n, ..., n+h-1` and return the predictions as a numpy array.

If `K == 0`, the model has only the constant and the trend.

### Example 1
**Input:** `y = [10, 12, 14, 16, 18]`, `period = 4`, `K = 0`, `h = 2`
**Output:** `array([20., 22.])`
**Explanation:** The data is a straight line with slope 2.

### Example 2
**Input:** `y = 100 + 0.5 t + 10 sin(2 pi t / 7)` for 70 points, `period = 7`, `K = 1`, `h = 7`
**Output:** the next 7 values of the same formula (the fit is exact).

### Constraints
- `n >= 2 * K + 2`, `period > 0`, `0 <= K <= 20`, `0 <= h <= 1000`
- Use numpy only.

### Hints
1. Write a helper `features(t)` that returns the matrix for any array of times. Use it for training and for the future.
2. `np.linalg.lstsq(X, y, rcond=None)[0]` gives the weights.
3. The future times continue the index: `np.arange(n, n + h)`.

### Solution explanation
Because the features depend only on time, the future feature matrix is known. We multiply it by the weights. There is no recursion, so errors do not build up. Time O(n * K^2) for the fit. Common bugs: restarting the time index at 0 for the future (the trend and the phase break), forgetting the constant column, and not using the same `period` for train and future.
