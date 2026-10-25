---
slug: expanding-target-encoding
title: Time-Safe Target Encoding
difficulty: Medium
type: function
tags: [pandas, target-encoding, leakage, groupby]
skills: [leakage, pandas-fluency]
packages: []
---
A table `df` is sorted by time (oldest row first). Each row has a category (a column named by `cat`) and a numeric target (a column named by `target`).

Write `expanding_target_encoding(df, cat, target, m=0.0)`. It returns a `Series` with the same index as `df`. For row `i` the value uses **only rows before `i`**:

- `prior_i` = mean of the target over **all** rows before `i` (any category). For the first row it is `NaN`.
- `sum_i`, `count_i` = sum and number of earlier targets **in the same category** as row `i`.
- Value = `(sum_i + m * prior_i) / (count_i + m)`.
- If `count_i + m == 0` (a new category and `m == 0`), the value is `prior_i`.
- If `prior_i` is `NaN` (first row), the value is `NaN`.

### Example 1
**Input:** `cat = [A, B, A, B, A, B]`, `y = [10, 50, 20, 60, 30, 70]`, `m = 0`

**Output:** `[NaN, 10, 10, 50, 15, 55]`

**Explanation:** Row 0 has no earlier rows. Row 1 is a new category B. With `m = 0` it gets the prior, the mean of earlier rows: 10. Row 2 is category A with one earlier A row (10), so its value is 10. Row 3 is category B with one earlier B row (50). Row 4: earlier A rows are 10 and 20, so 15. Row 5: earlier B rows are 50 and 60, so 55.

### Example 2
**Input:** the same data with `m = 2`

**Output:** `[NaN, 10, 23.33, 34.44, 25, 44.5]`

**Explanation:** Row 2 (category A): the prior is the mean of 10 and 50, which is 30. Its sum is 10 and its count is 1, so the value is `(10 + 2 × 30) / (1 + 2) = 23.33`. Row 1: no earlier B rows, so `(0 + 2 × 10) / (0 + 2) = 10`.

### Constraints
- 0 ≤ rows ≤ 10^5. `m ≥ 0`. Targets have no `NaN`.

### Hints
1. Per-category earlier sum: `df.groupby(cat)[target].cumsum() - df[target]`. Earlier count: `groupby(cat).cumcount()`.
2. Overall earlier mean: `(df[target].cumsum() - df[target]) / np.arange(n)`; the first value is `NaN` because of `0/0`.
3. Combine with the formula. Handle `count + m == 0` before dividing.

### Solution explanation
Everything is a running total minus the current row, so the current target never enters its own feature. The whole function is vectorized: O(n). Common bugs: using `transform('mean')` (leak), and `expanding().mean()` without `shift(1)`.
