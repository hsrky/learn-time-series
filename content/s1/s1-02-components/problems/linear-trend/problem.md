---
slug: linear-trend
title: Fit a Linear Trend
difficulty: Easy
type: function
tags: [numpy, trend, least-squares, from-scratch]
skills: [from-scratch, pandas-fluency]
packages: []
companies_style: [growth analytics]
---
Write `linear_trend(y)`. It fits the line `y = a + b·t` to the values by [[least squares]], where `t = 0, 1, 2, ...` is the position of each value. Return the tuple `(b, a)`: slope first, then intercept.

Missing values (`nan`) must be skipped, but each value keeps its **own position** `t`. Do not use `np.polyfit` (write the formula).

The formulas are:

- `b = Σ (t − t̄)(y − ȳ) / Σ (t − t̄)²`
- `a = ȳ − b·t̄`

where `t̄` and `ȳ` are the means over the valid points.

### Example 1
**Input:** `y = [100, 110, 125, 135, 150]`
**Output:** `(12.5, 99.0)`
**Explanation:** The slope is 12.5 per step and the line starts at 99 for t = 0.

### Example 2
**Input:** `y = [1, nan, 5]`
**Output:** `(2.0, 1.0)`
**Explanation:** The valid points are (t=0, y=1) and (t=2, y=5). The line through them has slope 2 and intercept 1.

### Constraints
- `2 <= len(y)`, and at least 2 valid points with different `t`.
- Return Python floats or numpy floats.

### Hints
1. Build `t = np.arange(len(y))` and a mask `ok = ~np.isnan(y)`.
2. Keep only `t[ok]` and `y[ok]`. Compute their means.
3. Use the two formulas with numpy sums. No loop is needed.

### Solution explanation
1. Mask out the nan values but keep the original positions.
2. `b` is the covariance of t and y divided by the variance of t (both as sums).
3. `a` makes the line pass through the point of means.

Time O(n), space O(n). Bug to avoid: building `t` from the valid points only (0, 1, 2...) changes the spacing when values are missing.
