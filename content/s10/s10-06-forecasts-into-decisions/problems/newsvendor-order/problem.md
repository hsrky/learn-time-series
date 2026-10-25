---
slug: newsvendor-order
title: Newsvendor Order Quantity
difficulty: Medium
type: function
tags: [newsvendor, quantile, decisions, numpy]
skills: [probabilistic-forecasting, ml-system-design]
packages: []
companies_style: [retail demand, perishable goods, food delivery]
---
A shop must choose an order quantity `q` before it knows the demand. You have demand **scenarios** (samples). Each unit short costs `cu` (underage). Each unit left over costs `co` (overage).

Write two functions.

**1. `expected_cost(q, samples, cu, co)`** returns the average over the samples of `cu * max(d - q, 0) + co * max(q - d, 0)`.

**2. `newsvendor_order(samples, cu, co)`** returns the best `q` among the sample values. Use the critical ratio `r = cu / (cu + co)`. Sort the samples. With `n` samples, let `k = ceil(r * n - 1e-9)` (at least 1). Return the `k`-th smallest value (1-based), the smallest value whose share of samples at or below it is at least `r`.

### Example 1
**Input:** `samples = [10, 20, 30, 40]`, `cu = 3`, `co = 1`
**Output:** `30`
**Explanation:** `r = 0.75`, `k = ceil(3.0) = 3`, the 3rd smallest value is 30. The average cost of q = 30 is 15. Ordering 20 costs 25, and ordering 40 also costs 15 (a tie, because the ratio is exactly 0.75). The rule picks the smaller value, 30.

### Example 2
**Input:** `samples = [5, 5, 5]`, `cu = 1`, `co = 1`
**Output:** `5`

### Constraints
- 1 ≤ number of samples ≤ 100 000. Samples are non-negative numbers.
- `cu > 0` and `co > 0`.

### Hints
1. The critical ratio is `cu / (cu + co)`.
2. Sort the samples with `np.sort`. The index of the `k`-th smallest is `k - 1`.
3. `k = max(1, math.ceil(r * n - 1e-9))`. The small number protects against floating-point error like 7.000000000000001.

### Solution explanation
The expected cost of an order `q` is lowest where the share of demand at or below `q` first reaches `cu / (cu + co)`. With samples, this is an empirical quantile. Sorting costs O(n log n). Common bugs: using `np.mean` (ignores the costs), using `np.quantile` with interpolation (the answer may not be a sample value, and it can be not exactly optimal), and mixing up `cu` and `co` (the ratio would be inverted).
