---
slug: ewma-from-scratch
title: EWMA From Scratch
difficulty: Medium
type: function
tags: [numpy, ewma, smoothing, from-scratch]
skills: [from-scratch]
packages: []
companies_style: [monitoring, demand forecasting]
---
Write `ewma(x, alpha)` without `pandas.ewm`. It returns a numpy array with the exponentially weighted moving average of the list `x`:

- `S[0] = x[0]`
- `S[t] = alpha * x[t] + (1 - alpha) * S[t-1]` for `t >= 1`

Missing values: if `x[t]` is `nan`, the average does not change: `S[t] = S[t-1]`. If `x[0]` is nan, `S` stays nan until the first real value. That first real value becomes the start value.

### Example 1
**Input:** `x = [10, 10, 20]`, `alpha = 0.4`
**Output:** `[10, 10, 14]`
**Explanation:** `S[2] = 0.4 · 20 + 0.6 · 10 = 14`.

### Example 2
**Input:** `x = [1, nan, 3]`, `alpha = 0.5`
**Output:** `[1, 1, 2]`
**Explanation:** The nan keeps the old value 1. Then `0.5 · 3 + 0.5 · 1 = 2`.

### Constraints
- `0 <= len(x) <= 10^5`; `0 < alpha <= 1`.
- Return a float numpy array of the same length as `x`.
- This uses a loop over time, which is normal here: each value depends on the previous one. O(n).

### Hints
1. Create an output array of the same length filled with nan.
2. Keep a variable `s` for the last smoothed value. Start with `s = nan`.
3. For each value: skip it if it is nan; if `s` is nan, set `s = value`; else apply the formula. Then store `s`.

### Solution explanation
1. Loop over the values once and keep the running `s`.
2. A nan input does not change `s`. The output at that position is the current `s` (which may still be nan at the start).
3. The first real value starts the average, then the formula applies.

Time O(n), space O(n). With `alpha = 1` the output copies the input (except for nan positions). Bug to avoid: using `S[0] = 0` as the start. That biases the early values toward 0.
