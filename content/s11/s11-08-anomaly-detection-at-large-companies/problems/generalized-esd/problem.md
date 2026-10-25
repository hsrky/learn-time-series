---
slug: generalized-esd
title: Generalized ESD Outlier Test
difficulty: Hard
type: function
tags: [anomaly-detection, outliers, statistics, scipy, ESD]
skills: [anomaly-detection, from-scratch-algorithms]
packages: [scipy]
companies_style: [monitoring, anomaly detection]
---
Twitter's anomaly detection method (S-H-ESD) ends with the **generalized ESD test** (Rosner, 1983). It finds up to `r` outliers in roughly normal data, without knowing how many there are. Implement it.

Write `generalized_esd(x, max_outliers, alpha=0.05)`. For `i = 1, 2, …, r` (`r = max_outliers`):

1. Compute `mean` and sample standard deviation `s` (`ddof=1`) of the **current** values (`n − i + 1` values remain).
2. Find the value farthest from the mean: `R_i = max |x − mean| / s`. Remove that value and remember its **original index**.
3. Compute the critical value
   `λ_i = (n − i) · t / sqrt((n − i − 1 + t²) · (n − i + 1))`,
   where `t` is the Student-t quantile `t.ppf(1 − p, n − i − 1)` with `p = alpha / (2 · (n − i + 1))`.

The number of outliers is the **largest** `i` for which `R_i > λ_i`. Return the original indices of the first `i` removed values as a **sorted list**. If no `R_i` is larger than its `λ_i`, return `[]`.

Stop early (return what you have) if fewer than 3 values remain or `s == 0`.

### Example 1
**Input:** `x = [10, 11, 9, 10, 10, 11, 9, 10, 100]`, `max_outliers = 2`
**Output:** `[8]`
**Explanation:** The value 100 is a clear outlier. After removing it, the rest is normal.

### Constraints
- 3 ≤ n ≤ 5 000. `1 ≤ max_outliers ≤ n // 2`. Values are finite floats.
- Use `scipy.stats.t.ppf`.

### Hints
1. Keep a list of the remaining indices. Each round compute mean and `std(ddof=1)` of the remaining values.
2. Use `np.argmax(np.abs(vals - mean))` to find the farthest value. Store `R_i` and the removed index.
3. After the loop, find the largest `i` with `R_i > λ_i`, and return `sorted(removed[:i])`.

### Solution explanation
The test removes the most extreme value one at a time, so a big outlier cannot hide a smaller one (this is called masking). The critical values `λ_i` come from the t distribution and are adjusted for repeated testing. The key detail is to pick the **largest** `i` that passes, not the first failure: a small outlier can still be detected after a larger one. Complexity: O(r · n). Common bugs: using `ddof=0`, stopping at the first `R_i ≤ λ_i`, and returning indices relative to the shrinking array.
