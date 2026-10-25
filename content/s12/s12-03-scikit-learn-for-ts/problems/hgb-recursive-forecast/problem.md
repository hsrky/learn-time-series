---
slug: hgb-recursive-forecast
title: Gradient Boosting with Recursive Forecasting
difficulty: Hard
type: forecast
tags: [scikit-learn, HistGradientBoostingRegressor, recursive-forecast, lag-features]
skills: [lag-features, recursive-forecasting, scikit-learn]
packages: [scikit-learn]
companies_style: [retail demand, global models]
---
A tree model has no built-in time. You must give it **lag features** and, to forecast many steps, feed its own predictions back as new lags. This is **recursive forecasting**.

Write `hgb_forecast(y, h, n_lags)`.

1. Build the training table: for each `t = n_lags … len(y)-1` the features are `[y[t-1], y[t-2], …, y[t-n_lags]]` and the target is `y[t]`.
2. Fit `sklearn.ensemble.HistGradientBoostingRegressor(max_iter=200, random_state=0)` on the table.
3. Forecast `h` steps. For each step, use the **last `n_lags` values** (real values first, then your own forecasts) in the same order `[newest, …, oldest]`, predict one value, and append it to the history.
4. Return the `h` forecasts as a numpy array.

The judge passes a case when your MAE is **at most 90%** of the MAE of the seasonal naive forecast.

### Example 1
**Input:** a weekly-seasonal series with noise, `h = 14`, `n_lags = 7`
**Output:** an array of 14 numbers that follows the weekly shape.

### Constraints
- `len(y) ≥ 4 · n_lags`. `1 ≤ h ≤ 30`. `1 ≤ n_lags ≤ 30`.
- Do not use the future values. The judge has them hidden.

### Hints
1. Create the lag matrix with `np.column_stack([y[n_lags - j: len(y) - j] for j in range(1, n_lags + 1)])`.
2. Keep a Python list `hist = list(y)`. The newest lags are `hist[-1], hist[-2], …`.
3. Inside the loop: `x = np.array(hist[-1: -n_lags - 1: -1]).reshape(1, -1)`; `p = model.predict(x)[0]`; `hist.append(p)`.

### Solution explanation
Gradient boosting learns the mapping from the last `n_lags` values to the next value. For several steps ahead we use the model again and again, each time adding its prediction to the history. This is simple and uses one model, but errors can add up over the horizon. Trees cannot extrapolate beyond the range of values they saw, so strong trends need differencing first (a good follow-up exercise). Complexity: one training run plus `h` predictions. Common bugs: using the lags in the wrong order, forgetting to append the forecast, and training on a shuffled table.
