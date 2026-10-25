---
slug: train-only-scaler
title: Standardize Without Leaking
difficulty: Easy
type: function
tags: [pandas, scaling, leakage]
skills: [leakage, pandas-fluency]
packages: []
---
A feature table `df` has a sorted `DatetimeIndex` and numeric columns. You must standardize every column, but **only the training rows may shape the scaler**.

Write `scale_with_train_stats(df, n_train)`:

1. The first `n_train` rows are the training rows.
2. For each column compute the **mean** and the **standard deviation** on the training rows only. Use the population formula (`ddof=0`). Ignore `NaN` values.
3. Return a table of the same shape with `(x - mean) / sd` for **all** rows (train and test).
4. If a column has `sd == 0` in the training rows, return `0.0` for that column in every row (not `inf` or `NaN`). `NaN` inputs stay `NaN`.

### Example 1
**Input:** one column `[10, 12, 14, 20]`, `n_train=3`

**Output:** `[-1.2247, 0, 1.2247, 4.899]`

**Explanation:** Train mean = 12, train sd = 1.633. The test value 20 becomes (20 − 12) / 1.633 = 4.899. It is not centered, and that is correct: it shows the test value is far from the training range.

### Constraints
- 1 ≤ `n_train` ≤ number of rows ≤ 10^5.
- Columns are numeric. They may contain `NaN`.

### Hints
1. Slice the training part with `df.iloc[:n_train]`.
2. `train.mean()` and `train.std(ddof=0)` skip `NaN` by default and return one number per column.
3. Replace zero standard deviations before dividing, for example with `sd.replace(0, np.nan)`, then fill the result with 0 where `sd` was 0.

### Solution explanation
1. Compute `mu` and `sd` from the first `n_train` rows only (vectorized per column).
2. Mark columns with `sd == 0`. Divide using a safe sd (use 1 where sd is 0) so no division by zero happens.
3. For constant columns, set non-`NaN` values to 0.

Time O(n·c) for n rows and c columns. A typical bug is calling `df.mean()` on the whole table, which leaks the test period into the scaler.
