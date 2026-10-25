---
slug: baseline-leaderboard
title: Baseline Leaderboard
difficulty: Easy
type: function
tags: [baseline, mae, model-comparison]
skills: [baseline-first, metrics, from-scratch]
packages: []
companies_style: [demand forecasting]
---
Before you build a complex model, you rank the simple ones. Write `leaderboard(train, test, m)`.

Forecast `len(test)` steps from `train` with each of the four methods below. Then compute the mean absolute error (MAE) of each forecast against `test`.

- `"mean"`: the mean of `train`.
- `"naive"`: the last value of `train`.
- `"seasonal_naive"`: the value one season (`m` steps) earlier, cycling through the last season (use `train[n - m + (j - 1) % m]` for step `j`).
- `"drift"`: `train[-1] + j * (train[-1] - train[0]) / (n - 1)`.

Return a dict with:

- `"mae"`: a dict `{method: mae rounded to 4 decimals}` for all four methods.
- `"best"`: the name of the method with the lowest MAE. On a tie, choose the first one in the order listed above.
- `"skill"`: `1 - MAE(best) / MAE(naive)`, rounded to 4 decimals. If `MAE(naive)` is 0, use `0.0`.

If `len(train) < m`, skip `seasonal_naive` (do not include it in `"mae"`).

### Example 1
**Input:** `train = [10, 20, 30, 40, 12, 22, 32, 42]`, `test = [14, 24, 34, 44]`, `m = 4`
**Output:** `{"mae": {"mean": 10.0, "naive": 14.0, "seasonal_naive": 2.0, "drift": 24.4286}, "best": "seasonal_naive", "skill": 0.8571}`
**Explanation:** Seasonal naive forecasts 12, 22, 32, 42, so every error is 2.

### Example 2
**Input:** `train = [1, 2, 3, 4, 5]`, `test = [6, 7]`, `m = 1`
**Output:** `best` is `"drift"` and the MAE of drift is 0.

### Constraints
- `2 <= len(train) <= 10^5`, `1 <= len(test) <= 1000`, `m >= 1`
- Compute the MAE as `mean(abs(test - forecast))`.

### Hints
1. Write one inner helper `forecast(method)` that returns an array for the given method.
2. Loop over the methods in the listed order and store the MAE in a dict.
3. Use `min(maes, key=maes.get)`. It returns the first minimum in dict order.

### Solution explanation
We build four forecasts, score them on the test period, and report the best. The skill score shows the lift over naive. Time is O(n + k * h) for k methods. Common bugs: scoring on the training period, fitting the mean on train + test (leakage), and changing the order of methods, which changes the tie-breaking.
