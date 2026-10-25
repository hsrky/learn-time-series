---
slug: seasonal-naive-backtest
title: Seasonal Naive Backtest
difficulty: Medium
type: function
tags: [backtest, seasonal-naive, MAE, walk-forward]
skills: [backtest, baseline-first, from-scratch]
packages: []
companies_style: [retail demand, baseline]
---
A seasonal naive forecast repeats the last full season. With season length `m`, the forecast for the next `h` steps after a training series `y[0..o-1]` is: step `i` (0-based) equals `y[o - m + (i % m)]`.

Run a backtest with `k` folds on a list `y`. Each fold forecasts `h` steps. The test windows are the **last** `k*h` points, split into `k` consecutive blocks of `h`. For the block that starts at position `o`, the training data is `y[:o]` (everything before the block).

Write `seasonal_naive_backtest(y, m, h, k)`. Return the **mean absolute error (MAE)** over all `k*h` forecast points.

### Example 1
**Input:** `y = [1, 2, 3, 1, 2, 3, 1, 2, 4]`, `m = 3`, `h = 3`, `k = 1`
**Output:** `0.3333333333333333`
**Explanation:** The test block is `[1, 2, 4]` and the training data is `[1, 2, 3, 1, 2, 3]`. The last season is `[1, 2, 3]`, so the forecast is `[1, 2, 3]`. Errors: 0, 0, 1. MAE = (0 + 0 + 1) / 3.

### Constraints
- `m ≥ 1`, `h ≥ 1`, `k ≥ 1`
- The first training window must have at least `m` points: `len(y) - k*h >= m`
- `h` can be larger than `m` (then the season repeats)

### Hints
1. Block `j` (0-based) starts at `o = len(y) - (k - j) * h`.
2. The forecast is the last `m` training values repeated: `[y[o - m + (i % m)] for i in range(h)]`.
3. Add up all absolute errors and divide by `k*h`.

### Solution explanation
Loop over the `k` origins. For each origin take the last `m` training values and repeat them to length `h` using `i % m`. Compare with the real block and add the absolute errors. Divide by the total number of points. Time O(k·h). Only training data (`y[:o]`) is used, so there is no leakage. A common bug is to use `y[o-m:o]` without wrapping when `h > m`, or to use data after the origin.
