---
slug: interval-score-coverage
title: Coverage, Width and Interval Score
difficulty: Medium
type: function
tags: [prediction-interval, coverage, winkler]
skills: [uncertainty, metrics, from-scratch]
packages: []
---
Write `interval_metrics(y, lower, upper, alpha)`. It evaluates prediction intervals with nominal level `1 - alpha` (for example `alpha=0.2` for an 80% interval). All three arrays have the same length.

Return a dictionary with:
- `"coverage"`: the fraction of points with `lower <= y <= upper` (borders count as inside).
- `"mean_width"`: the mean of `upper - lower`.
- `"interval_score"`: the mean of
  `(u − l) + (2/alpha)·(l − y)` if `y < l`, plus `(2/alpha)·(y − u)` if `y > u` (only one of the penalties can apply).
- `"calibration_gap"`: `coverage − (1 − alpha)`. Negative means overconfident.

If the arrays are empty, all values are `nan`. If an interval is reversed (`lower > upper`), swap the two ends before you compute anything for that point.

### Example 1
**Input:** `y=[100, 120, 85]`, `lower=[90, 90, 90]`, `upper=[110, 110, 110]`, `alpha=0.2`

**Output:** `coverage=0.333`, `mean_width=20.0`, `interval_score=(20 + 120 + 70)/3 = 70.0`, `calibration_gap=-0.467`

**Explanation:** Point 1 is inside: score 20. Point 2 is 10 above: 20 + 10×10 = 120. Point 3 is 5 below: 20 + 10×5 = 70.

### Constraints
- 0 ≤ length ≤ 10^5. `0 < alpha < 1`.

### Hints
1. Use `np.minimum(lower, upper)` and `np.maximum(lower, upper)` to fix reversed intervals.
2. Penalties: `np.maximum(l - y, 0)` and `np.maximum(y - u, 0)`.
3. `coverage = np.mean((y >= l) & (y <= u))`.

### Solution explanation
All parts are vectorized. The two `maximum` calls are zero when the point is inside, so no `if` is needed. Time O(n). The interval score rewards narrow intervals and punishes misses by `2/alpha`, which is larger for high-confidence intervals.
