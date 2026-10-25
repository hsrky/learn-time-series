---
slug: generalized-esd
title: Generalized ESD Outlier Test
difficulty: Hard
type: function
tags: [anomaly, statistics, scipy]
skills: [anomaly-detection]
packages: [scipy]
companies_style: []
---
Implement Rosner's **generalized ESD test**. Given a list `values` (the data are roughly normal), a maximum number of outliers `r` and a level `alpha`, return the **sorted positions** of the outliers.

For `i = 1, 2, ..., r`:

1. Using the points that are still left (call their count `m = n - i + 1`), compute the mean and the **sample** standard deviation `s` (divide by `m - 1`).
2. Find the point with the largest `abs(x - mean)`. Set `R_i = abs(x - mean) / s`. Remove that point and remember its original position.
3. Compute `p = 1 - alpha / (2 * m)` and `t` = the Student t quantile at `p` with `m - 2` degrees of freedom. Then `lambda_i = (m - 1) * t / sqrt((m - 2 + t**2) * m)`.

The number of outliers is the **largest** `i` with `R_i > lambda_i` (0 if there is none). Return the sorted positions of the first that many removed points.

Stop early if fewer than 3 points would be left. If `s == 0`, there are no outliers. `scipy.stats.t.ppf(p, df)` gives the quantile.

### Example 1
**Input:** `values = [10, 11, 9, 10, 12, 10, 11, 9, 10, 40]`, `r = 3`, `alpha = 0.05`
**Output:** `[9]`
**Explanation:** The value 40 (position 9) is far from the others. After removing it, the next R values are too small.

### Example 2
**Input:** `values = [5, 5, 5, 5]`, `r = 2`
**Output:** `[]`
**Explanation:** The standard deviation is 0, so there are no outliers.

### Constraints
- 3 <= len(values) <= 2000
- 1 <= r <= 50
- 0 < alpha < 1

### Hints
1. Keep a list of the original positions, and remove the most extreme one in each step.
2. Store each R_i and lambda_i in lists, then look for the largest i with R_i > lambda_i.
3. Do not stop at the first i where R_i <= lambda_i. A later step can still pass the test (masking).

### Solution explanation
**Approach.** Repeat r times: compute mean and sample std of the remaining points, find the farthest point, store R, remove the point, compute λ. At the end, choose the largest i with R_i > λ_i. The first i removed points are the outliers.

**Why the "largest i" rule.** If two outliers are close together they mask each other: the first R is small. A later step, after one of them is removed, may pass. So we cannot stop at the first failure.

**Complexity.** Each step is O(n), so the total is O(r · n) time and O(n) space (plus the t quantile calls, O(r)).

**Common bugs.** Using the population std; wrong degrees of freedom (`m - 2`); stopping early; returning positions in removal order instead of sorted.
