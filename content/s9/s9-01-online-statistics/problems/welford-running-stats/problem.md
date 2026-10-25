---
slug: welford-running-stats
title: Running Mean and Variance
difficulty: Medium
type: class
tags: [streaming, class, statistics]
skills: [streaming-algorithms, from-scratch]
packages: []
companies_style: []
---
Design a class `RunningStats` that processes numbers one by one.

- `update(x)`: add the number `x` and return a tuple `(mean, variance)` for **all numbers seen so far**.
- The mean is the average of the values. The variance is the **sample variance** (divide the sum of squared deviations by `n - 1`). When only one value has been seen, the variance is `0.0`.

Use O(1) memory (do not store the values) and make it numerically stable, because the tests use large numbers with a small spread.

### Example 1
**Input:** `r = RunningStats()`; updates with `4, 8, 6`
**Output:** `[(4.0, 0.0), (6.0, 8.0), (6.0, 4.0)]`
**Explanation:** After 4: mean 4, variance 0. After 8: mean 6, variance 8. After 6: mean 6, variance 4.

### Constraints
- 0 <= number of updates <= 10^5
- -10^12 <= x <= 10^12 (floats)

### Hints
1. Store `n`, `mean` and `M2` (sum of squared deviations).
2. On each update: `delta = x - mean`, `mean += delta / n`, `M2 += delta * (x - mean)`.
3. Sample variance is `M2 / (n - 1)` when `n > 1`.

### Solution explanation
**Approach.** Welford's algorithm: three numbers `n`, `mean`, `M2`. Each update changes them in a few operations.

**Why it works.** `delta * (x - new_mean)` is the exact change of the sum of squared deviations when a value joins the group. It never subtracts two huge numbers, so rounding errors stay small.

**Complexity.** O(1) time per update and O(1) memory in total.

**Common bugs.** Using the sum-of-squares formula (fails on large values); updating `M2` with the new mean twice; dividing by `n - 1` when `n = 1`.
