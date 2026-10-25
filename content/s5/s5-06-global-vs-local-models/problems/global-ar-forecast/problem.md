---
slug: global-ar-forecast
title: One Global AR Model for Many Series
difficulty: Medium
type: function
tags: [global-model, numpy, lstsq, scaling]
skills: [scale, from-scratch]
packages: []
---
Write `global_ar_forecast(series, p)`. `series` is a dictionary `{series_id: list of numbers}`. Series have different levels and lengths.

Train **one** model on all series together:

1. For every series and every window `y[i:i+p]` with the next value `y[i+p]` as target (all windows that fit), compute the scale `s = mean(|window|)`. If `s == 0`, use `s = 1`.
2. Features are the window divided by `s` plus a constant `1`. The target is `y[i+p] / s`.
3. Stack the rows of all series and fit the weights with `np.linalg.lstsq(A, target, rcond=None)`.
4. For each series with at least `p` values, take its **last** `p` values, compute `s` the same way, predict `(window / s, 1) @ w`, and multiply by `s`.

Return a dictionary `{series_id: one-step-ahead forecast}`. A series with fewer than `p` values gets `nan`. If there are no training rows at all, return `nan` for every series.

### Example 1
**Input:** `series = {"a": [1, 2, 3, 4, 5], "b": [10, 20, 30, 40, 50]}`, `p = 2`

**Output:** `{"a": 6.0, "b": 60.0}`

**Explanation:** After dividing by the window mean, both series follow the same rule, so one model fits both. The forecasts continue each line.

### Constraints
- Up to 1000 series, each up to 1000 points. `1 ≤ p ≤ 50`.

### Hints
1. Loop over series; use a helper that returns the scaled rows of one series.
2. Do not scale the intercept column. Append it after dividing the lags by `s`.
3. `np.vstack` the rows and `np.concatenate` the targets. Remember the scale again when you predict.

### Solution explanation
Scaling each window by its own mean puts all series in the same range, so one linear rule can describe all of them (the idea behind global models). The scale is computed from the window itself, so there is no leak. Time O(rows·p²). Common bugs: scaling the intercept, using the series mean instead of the window mean, and forgetting to multiply the prediction by `s`.
