---
slug: seasonal-difference
title: Seasonal and Regular Differencing
difficulty: Easy
type: function
tags: [differencing, seasonality, pandas]
skills: [pandas-fluency, from-scratch]
packages: []
companies_style: [retail demand]
---
You have a pandas `Series` `s` with a repeating season of length `m` (for example `m = 7` for daily data with a weekly pattern).

Write `difference(s, m=0, d=0)` that makes the series closer to [[stationary]]:

1. If `m > 0`: take **one seasonal difference**: `s[t] - s[t-m]`.
2. Then take `d` ordinary differences (`x[t] - x[t-1]`), one after the other.
3. Drop the leading `NaN` values that the differences create.

Always do the seasonal step first. Return a `Series` with the original index labels that remain. If `m = 0` and `d = 0`, return the series unchanged.

### Example 1
**Input:** `s = pd.Series([10, 20, 30, 40, 12, 22, 32, 42])`, `m = 4`
**Output:** `[2, 2, 2, 2]` with index `4, 5, 6, 7`.
**Explanation:** 12-10, 22-20, 32-30, 42-40.

### Example 2
**Input:** `s = pd.Series([1, 4, 9, 16, 25])`, `d = 2`
**Output:** `[2, 2, 2]` with index `2, 3, 4`.
**Explanation:** First difference: 3, 5, 7, 9. Second difference: 2, 2, 2.

### Constraints
- `0 <= m < len(s)`, `d >= 0`
- The result length is `len(s) - m - d` (never negative; if there are not enough points, return an empty series).
- Do not use Python loops over rows.

### Hints
1. pandas has `Series.diff(periods)`. A seasonal difference is `diff(m)`.
2. Call `diff(1)` `d` times in a loop over `d` (a loop over steps is fine, not over rows).
3. Finish with `.dropna()`. Be careful: only drop the NaN values that you created. Your input has none.

### Solution explanation
`s.diff(m)` returns `s[t] - s[t-m]` and puts `NaN` in the first `m` places. Each ordinary `diff()` adds one more `NaN`. After all steps, `dropna()` removes exactly `m + d` leading values. Time O(n * (d + 1)), space O(n). Common bugs: forgetting `dropna()`, using `diff(m)` where `diff(1)` is needed, and dropping `NaN` between steps (which shifts the positions).
