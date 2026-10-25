---
slug: top-down-proportions
title: Top-Down Forecast with Proportions
difficulty: Medium
type: function
tags: [hierarchical, top-down, proportions, numpy]
skills: [from-scratch, leakage]
packages: []
companies_style: [retail demand]
---
You forecast the **total** of a group of series and split it into the bottom series with historical proportions.

Write `top_down(history, total_forecast, method="avg_of_props")`.

- `history`: a 2D array with `T` rows (periods) and `m` columns (bottom series). All values are positive. The total of a period is the row sum.
- `total_forecast`: a list of `h` forecasts of the total.
- `method`:
  - `"avg_of_props"` (average of proportions): `p_j = mean over t of ( history[t, j] / total[t] )`
  - `"prop_of_avgs"` (proportion of averages): `p_j = mean(history[:, j]) / mean(total)`

Return a numpy array of shape `(h, m)`: row `k` is `total_forecast[k] * p`. Raise `ValueError` for another method name.

The proportions always sum to 1, so each row sums to the total forecast.

### Example 1
**Input:** `history = [[30, 20], [40, 20]]`, `total_forecast = [66]`, `method = "prop_of_avgs"`
**Output:** `array([[42., 24.]])`
**Explanation:** The means are 35 and 20, the mean total is 55. The proportions are 0.636 and 0.364. 66 * 0.636 = 42 and 66 * 0.364 = 24.

### Example 2
**Input:** the same history with `method = "avg_of_props"`, `total_forecast = [60, 70]`
**Output:** `[[38, 22], [44.33, 25.67]]` (rounded)
**Explanation:** The shares in period 1 are (0.6, 0.4). In period 2 they are (0.667, 0.333). Their mean is (0.633, 0.367). Then 60 * 0.633 = 38 and 70 * 0.633 = 44.33.

### Constraints
- `1 <= T <= 10^4`, `1 <= m <= 100`, `0 <= h <= 1000`
- Use the **history only** (no future data) to compute the proportions.

### Hints
1. `total = history.sum(axis=1)`.
2. For the average of proportions use `(history / total[:, None]).mean(axis=0)`.
3. `np.outer(total_forecast, p)` builds the result.

### Solution explanation
The proportions are computed once from the training history. The forecast of every bottom series is then a fixed share of the total forecast. The result is coherent by construction. Time O(T * m + h * m). The method works well when shares are stable. If shares drift, the lower levels become inaccurate. Common bugs: using the test period to compute proportions (leakage) and dividing by the wrong axis.
