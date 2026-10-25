---
slug: zscore-columns
title: Standardize Each Sensor
difficulty: Easy
type: function
tags: [numpy, broadcasting, nan]
skills: [pandas-fluency]
packages: []
companies_style: [IoT sensors]
---
A 2D numpy array `data` has one row per day and one column per sensor. Some values are `nan` (missing).

Write `zscore_columns(data)`. For each column, return `(x - mean) / std`. Use the mean and the standard deviation of that column, **ignoring nan**. Use the population standard deviation (`ddof=0`, the numpy default).

- A `nan` input stays `nan` in the output.
- If a column has standard deviation 0, return 0.0 for its non-missing values.

### Example 1
**Input:** `data = np.array([[1.0, 5.0], [3.0, 5.0]])`
**Output:** `array([[-1., 0.], [1., 0.]])`
**Explanation:** Column 0 has mean 2 and std 1. Column 1 has std 0, so its values become 0.

### Constraints
- `data` has shape `(n, m)` with `1 <= n, m <= 1000`.
- Do not use a Python loop over rows or columns.

### Hints
1. Compute one mean and one std per column with `axis=0`.
2. Use `np.nanmean` and `np.nanstd` so the nan values are skipped.
3. Replace a zero std by 1 before you divide. Then the numerator is 0 and the result is 0.

### Solution explanation
1. `mean = np.nanmean(data, axis=0)` and `std = np.nanstd(data, axis=0)`. Both have shape `(m,)`.
2. `safe = np.where(std == 0, 1.0, std)` avoids division by zero.
3. `(data - mean) / safe` uses broadcasting. A nan stays nan.

Time O(n·m), space O(n·m). Bug to avoid: `np.std` instead of `np.nanstd` gives nan for the whole column.
