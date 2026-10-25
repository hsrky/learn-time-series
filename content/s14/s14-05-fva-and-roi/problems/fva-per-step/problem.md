---
slug: fva-per-step
title: Forecast Value Add per Process Step
difficulty: Medium
type: function
tags: [staff, FVA, WAPE, forecast-process]
skills: [staff, metrics, baseline-first]
packages: []
companies_style: [demand planning, forecast process review]
---
A planning process makes the final forecast in several steps. For example: (1) a naive forecast, (2) a statistical model, (3) a machine-learning model, (4) the analyst's manual override. **Forecast value add (FVA)** asks: does each step make the forecast better than the step before?

Write `fva_by_step(actual, steps)`.

- `actual` is a list of real values (sum > 0).
- `steps` is a list of `(name, forecast_list)` pairs in process order. The first step is the baseline (for example naive). Each forecast list has the same length as `actual`.

For each step compute:

- `wape` = sum(|actual − forecast|) / sum(actual)
- `fva_prev` = `wape` of the previous step − `wape` of this step (positive = this step helped). For the first step, use `0.0`.
- `fva_naive` = `wape` of the first step − `wape` of this step. For the first step, use `0.0`.
- `adds_value` = `True` if `fva_prev > 1e-12`, else `False` (the first step is always `False`).

Return a DataFrame with columns `step, wape, fva_prev, fva_naive, adds_value` in the same order as `steps`, with index `0, 1, 2, ...`.

### Example 1
**Input:**
```
actual = [100, 100]
steps = [("naive", [90, 110]), ("model", [95, 105]), ("override", [80, 120])]
```
**Output:**
```
step      wape   fva_prev  fva_naive  adds_value
naive     0.10   0.00      0.00       False
model     0.05   0.05      0.05       True
override  0.20  -0.15     -0.10       False
```
**Explanation:** The model halves the error. The manual override makes it four times worse than the model: it destroys value.

### Constraints
- 1 ≤ number of steps ≤ 20
- 1 ≤ len(actual) ≤ 10^5, all forecasts have the same length

### Hints
1. Write a small helper for WAPE with numpy arrays.
2. Compute the WAPE of every step first. Then `fva_prev` is the previous WAPE minus this WAPE.
3. For the first step, set both FVA values to 0.0 and `adds_value` to False.

### Solution explanation
FVA compares each step with the one before it, and with the naive baseline. A step that does not add value (negative or zero `fva_prev`) should be removed or fixed. This is the most direct way to show whether manual overrides or complex models help. Time O(steps · n). Common bug: comparing a step with the final forecast instead of the previous step, or using the mean of daily percentage errors instead of the ratio of sums.
