---
slug: hgb-lag-forecast
title: Gradient Boosting Forecast with Lag Features
difficulty: Hard
type: forecast
tags: [scikit-learn, gradient-boosting, lags, recursive, trend]
skills: [baseline-first, leakage, from-scratch]
packages: [scikit-learn]
companies_style: [retail demand, web traffic]
---
Write `forecast(y_train, horizon)`. It receives a daily series `y_train` (1-D array, weekly season of 7 days, with an upward or downward **trend**) and must return a `numpy` array with `horizon` forecasts for the days that follow.

Use `sklearn.ensemble.HistGradientBoostingRegressor` with lag features. Your forecast is judged on hidden future values:

- **Pass** if your MAE is at most **90%** of the MAE of the **seasonal naive** forecast (repeat the last 7 days). The message shows both scores.
- The output must have `horizon` finite numbers.

Warning: a tree model cannot predict values outside the range of its training targets. If you train on levels, your forecast will lag behind the trend and you will not beat the baseline.

### Example 1
**Input:** `y_train` = 300 days of `40 + 0.2·t + 6·sin(2πt/7) + noise`, `horizon = 14`

**Output:** an array of 14 numbers that continue the trend and the weekly wave.

**Explanation:** Seasonal naive repeats the last week and misses the trend. A good model captures both.

### Constraints
- 60 ≤ len(`y_train`) ≤ 1000, 1 ≤ `horizon` ≤ 28.
- Use `random_state=0`, `early_stopping=False` and at most 100 iterations so the run is fast in the browser.

### Hints
1. Make a table with features such as `lag_1`, `lag_2`, `lag_7`, `lag_14`, a shifted rolling mean and the weekday (`i % 7`). Drop the first 14 rows.
2. Do not predict the level. Predict `y[i] − y[i−7]`, and express the lag features relative to `y[i−7]`.
3. Forecast recursively: append each prediction to the history and compute the features for the next step from the history.

### Solution explanation
Differencing against lag 7 removes the trend from the target and keeps it in the training range of the trees, so the model only has to learn the weekly pattern and small corrections. Features are built from `h[:i]` only (no leakage). The recursive loop feeds predictions back into the history. Training is O(rows × iterations × features). Typical bugs: training on levels (flat forecast), using the true future in the recursive loop, and early stopping with a random validation split.
