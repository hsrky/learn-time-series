---
slug: walk-forward-mae
title: Walk-Forward Evaluator by Horizon Step
difficulty: Medium
type: function
tags: [backtest, mae, horizon]
skills: [backtest, from-scratch]
packages: []
---
Write `walk_forward_mae(y, forecaster, initial, horizon, step=1)`.

- `y` is a 1-D `numpy` array.
- `forecaster(train, h)` is a function you must call. It gets the training array and the horizon `h`. It returns an array of `h` predictions.
- Create folds like this. The first training part is `y[:initial]`. The test part is the next `horizon` values. Then move the origin by `step`. Use **expanding** training windows and only **complete** folds.
- For every fold compute the absolute errors of the `horizon` steps.
- Return a `numpy` array of length `horizon`: the **mean absolute error at each horizon step**, averaged over all folds.
- If no fold fits, return an array of `NaN` with length `horizon`.

Never pass test values to the forecaster.

### Example 1
**Input:** `y = [1, 2, 3, 4, 5, 6]`, naive forecaster (repeat the last value), `initial=3`, `horizon=2`, `step=1`

**Output:** `[1.0, 2.0]`

**Explanation:** Fold 1: train `[1,2,3]` predicts `[3,3]`. The truth is `[4,5]`, so the errors are `[1,2]`. Fold 2: train `[1,2,3,4]` predicts `[4,4]`. The truth is `[5,6]`, so the errors are `[1,2]`. The mean per step is `[1.0, 2.0]`. No third fold fits.

### Constraints
- 1 ≤ `initial` < len(`y`) ≤ 10^4, `horizon ≥ 1`, `step ≥ 1`.
- `forecaster` is deterministic.

### Hints
1. Loop over `end` from `initial` while `end + horizon <= len(y)`.
2. Call `forecaster(y[:end], horizon)`. Store `np.abs(y[end:end+horizon] - pred)`.
3. Stack the errors in a 2-D array and take `mean(axis=0)`.

### Solution explanation
For each origin `end` build the prediction from the past only, collect the absolute errors in a list, and average column by column. Time O(folds × cost of forecaster). The result tells how the error grows with the horizon step. Common bugs: passing `y[:end+horizon]` to the forecaster (leak), and averaging over everything into one number.
