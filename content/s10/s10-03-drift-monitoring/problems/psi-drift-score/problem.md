---
slug: psi-drift-score
title: Population Stability Index
difficulty: Medium
type: function
tags: [monitoring, drift, numpy, PSI]
skills: [monitoring, numpy-fluency]
packages: []
companies_style: [model monitoring, credit risk]
---
Implement the **Population Stability Index** between a training sample (`expected`) and a recent sample (`actual`) of one numeric feature.

Write `psi(expected, actual, bins=10, eps=1e-4)`.

1. Build `bins - 1` **inner edges**: the quantiles of `expected` at `k / bins` for `k = 1 … bins-1` (use `np.quantile`, default method).
2. A value `x` goes into bin number `np.searchsorted(inner, x, side="right")`. This gives bins `0 … bins-1`. The first and last bins are open on the outside.
3. Compute the share of each sample in each bin (count / sample size) for `expected` (`e`) and `actual` (`a`).
4. Clip every share to at least `eps`.
5. Return `sum((a - e) * ln(a / e))` as a Python float.

### Example 1
**Input:** `expected = [1,2,3,4,5,6,7,8]`, `actual = [1,2,3,4,5,6,7,8]`, `bins=4`
**Output:** `0.0`
**Explanation:** The two samples are the same, so every bin share is equal.

### Example 2
**Input:** `expected = [1,2,3,4,5,6,7,8]`, `actual = [7,7,8,8]`, `bins=2`
**Output:** about `4.6042`
**Explanation:** The inner edge is the median 4.5. Expected shares are (0.5, 0.5). All actual values are above it: shares (0, 1), clipped to (0.0001, 1). The sum is about 4.604.

### Constraints
- 1 ≤ `bins` ≤ 50. Samples have at least 1 value each. Values are finite.
- `expected` may contain ties; this can make bins unequal. That is fine, follow the rules above.

### Hints
1. `np.quantile(expected, np.linspace(0, 1, bins + 1)[1:-1])` gives the inner edges.
2. `np.searchsorted(inner, values, side="right")` gives the bin of each value. `np.bincount(..., minlength=bins)` counts them.
3. `np.clip(shares, eps, None)` then `np.sum((a - e) * np.log(a / e))`.

### Solution explanation
Bins come only from the training data, so they stay fixed over time. Count both samples in the same bins, turn counts into shares, protect against zero with `eps`, and add up the per-bin terms. Each term `(a − e)·ln(a/e)` is zero or positive, so PSI ≥ 0. Complexity: O((n + m) log bins) after one quantile computation O(n log n). Common bugs: building edges from `actual`, forgetting `minlength` (a bin with no values disappears and the arrays no longer align), and using `log10`.
