---
slug: ridge-lag-backtest-gap
title: Backtest with TimeSeriesSplit and a Gap
difficulty: Medium
type: function
tags: [scikit-learn, TimeSeriesSplit, backtest, lag-features, leakage]
skills: [backtesting, leakage-free-features, scikit-learn]
packages: [scikit-learn]
companies_style: [demand forecasting, model validation]
---
Build a leakage-free **walk-forward backtest** with scikit-learn.

Write `backtest_mae(y, n_lags, n_splits, gap)`.

1. Make a supervised table. For each time `t = n_lags … len(y)-1`, the row is `X[t] = [y[t-1], y[t-2], …, y[t-n_lags]]` and the target is `y[t]`. (Column `j` is lag `j+1`.)
2. Split the rows with `sklearn.model_selection.TimeSeriesSplit(n_splits=n_splits, gap=gap)`. Use default `test_size`. The split works on the **row order** of the table, so rows are never shuffled.
3. For each split fit `sklearn.linear_model.LinearRegression()` on the training rows and predict the test rows.
4. Return the **mean over splits** of the mean absolute error (MAE) of each split, as a float.

The `gap` removes the last `gap` rows before each test fold from training. It is used when the target at time `t` uses information that overlaps with later rows (for example, a target made from a rolling sum).

### Example 1
**Input:** `y = [1, 2, 3, ..., 40]`, `n_lags = 2`, `n_splits = 3`, `gap = 0`
**Output:** about `0.0`
**Explanation:** The series is a perfect line, so a linear model on lags predicts it exactly.

### Constraints
- `len(y) - n_lags` rows must be enough for the splits: at least `(n_splits + 1) · 2 + gap` rows.
- `n_lags ≥ 1`, `n_splits ≥ 2`, `gap ≥ 0`.

### Hints
1. Build `X` with `np.column_stack([y[n_lags - j : len(y) - j] for j in range(1, n_lags + 1)])` and `target = y[n_lags:]`.
2. `for tr, te in TimeSeriesSplit(n_splits=n_splits, gap=gap).split(X):` gives integer index arrays.
3. Use `np.mean(np.abs(pred - target[te]))` per fold and average the folds.

### Solution explanation
`TimeSeriesSplit` always trains on the past and tests on the next block, and with `gap > 0` it skips the rows right before the test block. This is a walk-forward (expanding window) backtest. The lag table is built once; lags only look backwards, so a row never contains values from its own future. Complexity: one linear regression per fold. Common bugs: shuffling, off-by-one in the lag columns (lag 1 must be `y[t-1]`), passing `y` instead of the table to `split`, and averaging the errors of all rows instead of averaging per-fold MAEs.
