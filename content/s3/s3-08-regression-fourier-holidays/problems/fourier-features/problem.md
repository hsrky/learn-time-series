---
slug: fourier-features
title: Fourier Features for Seasonality
difficulty: Medium
type: function
tags: [fourier, seasonality, feature-engineering, numpy]
skills: [from-scratch, pandas-fluency]
packages: []
companies_style: [retail demand, energy load]
---
Build Fourier features, the columns that let a linear regression learn a smooth repeating season.

Write `fourier_features(t, period, K)`.

- `t`: a list or array of time values (for example `0, 1, 2, ...`; they may be any numbers, also not sorted).
- `period`: the length of one season in the same units as `t` (for example 7 for weekly data on daily steps, 365.25 for a yearly cycle).
- `K`: the number of harmonics (`K >= 0`).

Return a numpy array with shape `(len(t), 2 * K)`. The columns are, in this order:

`sin(2*pi*1*t/period), cos(2*pi*1*t/period), sin(2*pi*2*t/period), cos(2*pi*2*t/period), ..., sin(2*pi*K*t/period), cos(2*pi*K*t/period)`

If `K == 0`, return an array of shape `(len(t), 0)`.

Also write `fourier_names(prefix, K)` that returns the list of column names `["{prefix}_sin1", "{prefix}_cos1", ..., "{prefix}_sinK", "{prefix}_cosK"]`.

### Example 1
**Input:** `fourier_features([0, 1, 2], 4, 1)`
**Output:** `array([[0., 1.], [1., 0.], [0., -1.]])` (up to tiny rounding)
**Explanation:** With period 4: sin(pi/2) = 1, cos(pi/2) = 0, then sin(pi) = 0, cos(pi) = -1.

### Example 2
**Input:** `fourier_names("week", 2)`
**Output:** `["week_sin1", "week_cos1", "week_sin2", "week_cos2"]`

### Constraints
- `0 <= len(t) <= 10^5`, `0 <= K <= 50`, `period > 0`
- Return floats. No Python loop over the rows of `t` (a loop over `k` is fine).

### Hints
1. Convert `t` to a float array. Then `2 * np.pi * k * t / period` is the angle for harmonic `k`.
2. Make a list of columns, two for each `k`, and join them with `np.column_stack`.
3. For `K == 0` return `np.empty((len(t), 0))`.

### Solution explanation
Each harmonic is a wave with `k` cycles per period. The regression gives each wave a weight. Together they can draw any smooth repeating shape. Time O(n * K). Common bugs: swapping the sin and cos order, forgetting the factor `2*pi`, and using `k` from 0 (a column of zeros and ones).
