---
slug: integrate-forecast
title: Undo Differencing for a Forecast
difficulty: Medium
type: function
tags: [arima, differencing, integration]
skills: [from-scratch]
packages: []
companies_style: [forecasting take-home]
---
An ARIMA model with `d` differences predicts the **differenced** series. You must turn these forecasts back into forecasts of the original series. This step is called **integration**.

Write `integrate_forecast(history, diff_forecast, d)`.

- `history`: the original series (a list of numbers, not differenced).
- `diff_forecast`: forecasts of the `d`-th difference of the series.
- `d`: the number of differences, `0 <= d <= 3`.

Return a numpy array with forecasts of the original series, one for each value in `diff_forecast`.

How: let `L_j` be the **last value** of the `j`-th difference of the history (`L_0` is the last value of the history itself). Start with `x = diff_forecast`. For `j = d-1, d-2, ..., 0`: replace `x` by `L_j + cumsum(x)`. The final `x` is the answer. If `d == 0`, return `diff_forecast` unchanged.

Raise `ValueError` if `len(history) < d` (not enough data for `d` differences).

### Example 1
**Input:** `integrate_forecast([1, 4, 9, 16], [2, 2, 2], 2)`
**Output:** `array([25., 36., 49.])`
**Explanation:** The second difference of squares is 2. `L_1 = 16 - 9 = 7`, `L_0 = 16`. First differences: `7 + cumsum([2,2,2]) = [9, 11, 13]`. Levels: `16 + cumsum([9, 11, 13]) = [25, 36, 49]`.

### Example 2
**Input:** `integrate_forecast([100], [2, 1.6, 1.28], 1)`
**Output:** `array([102., 103.6, 104.88])`

### Constraints
- `0 <= d <= 3`, `len(history) >= d`, `0 <= len(diff_forecast) <= 1000`
- Use `np.diff` and `np.cumsum`. Do not loop over the forecast values.

### Hints
1. Compute `L_j` with `np.diff(history, n=j)[-1]` (for `j = 0` use `history[-1]`).
2. Build the list `[L_0, ..., L_{d-1}]` first.
3. Go from the highest difference down to the original level, applying `L_j + np.cumsum(x)`.

### Solution explanation
Each integration step undoes one difference: the cumulative sum of the changes, added to the last known value of the level below. We need d of these steps, from the d-th difference down to the original series. Time O(d * (n + h)). Common bugs: using the last value of the original series at every step (you need the last value of each differenced series), and applying `cumsum` in the wrong order.
