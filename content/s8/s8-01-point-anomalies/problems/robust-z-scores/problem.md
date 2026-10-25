---
slug: robust-z-scores
title: Robust Z-Score with Median and MAD
difficulty: Easy
type: function
tags: [anomaly, mad, numpy]
skills: [anomaly-detection]
packages: []
companies_style: []
---
Write `robust_anomalies(values, threshold=3.5)`. It returns the positions of anomalies found with the **modified z-score**.

1. Let `m` be the median of `values`.
2. Let `mad` be the median of `abs(values - m)`.
3. If `mad > 0`: the robust score is `0.6745 * (x - m) / mad`. A point is an anomaly when `abs(score) > threshold`.
4. If `mad == 0` (more than half of the values are equal): a point is an anomaly when `x != m`.

Return the positions in increasing order as a list of ints.

### Example 1
**Input:** `values = [10, 12, 11, 13, 40]`
**Output:** `[4]`
**Explanation:** Median 12, MAD 1. The score of 40 is 0.6745 * 28 = 18.9 which is above 3.5.

### Example 2
**Input:** `values = [5, 5, 5, 5, 9, 5]`
**Output:** `[4]`
**Explanation:** The MAD is 0, so every value that is not equal to the median 5 is an anomaly.

### Constraints
- 1 <= len(values) <= 10^5
- values are numbers

### Hints
1. `np.median` gives the median; use it twice.
2. Use `np.abs(x - m)` for the distances.
3. Handle `mad == 0` before dividing.

### Solution explanation
**Approach.** Compute the median, then the MAD, then the score of each point in one vectorised step.

**Why it works.** The median and MAD change very little when a few values are extreme, so the spike cannot hide itself.

**Complexity.** Two medians cost O(n log n) time (or O(n) with selection). Extra space is O(n).

**Common bugs.** Forgetting the special case `mad == 0`; using the mean instead of the median; using `<` instead of `>`.
