---
slug: simple-exp-smoothing
title: Simple Exponential Smoothing
difficulty: Easy
type: function
tags: [ses, exponential-smoothing, from-scratch]
skills: [from-scratch]
packages: []
companies_style: [inventory planning]
---
Implement simple exponential smoothing (SES) without a library.

Write `ses(y, alpha, h)`. Use `l[0] = y[0]` and, for `t >= 1`:

`l[t] = alpha * y[t] + (1 - alpha) * l[t-1]`

Return a dict with two lists:

- `"level"`: the levels `l[0], ..., l[n-1]` (length `n`).
- `"forecast"`: `h` copies of the last level `l[n-1]`.

### Example 1
**Input:** `ses([10, 14, 12, 16], 0.5, 2)`
**Output:** `{"level": [10.0, 12.0, 12.0, 14.0], "forecast": [14.0, 14.0]}`
**Explanation:** 0.5 * 14 + 0.5 * 10 = 12, then 0.5 * 12 + 0.5 * 12 = 12, then 0.5 * 16 + 0.5 * 12 = 14.

### Example 2
**Input:** `ses([5, 5, 5], 0.3, 3)`
**Output:** `{"level": [5.0, 5.0, 5.0], "forecast": [5.0, 5.0, 5.0]}`

### Constraints
- `1 <= len(y) <= 10^5`, `0 <= alpha <= 1`, `h >= 0`
- Return plain lists of floats.

### Hints
1. Keep a variable `level`. Start it with `y[0]` and append it to the output.
2. For each next value, update `level = alpha * value + (1 - alpha) * level`.
3. The forecast is `[level] * h`.

### Solution explanation
SES is a recursion over time: one pass, one update per value. Time O(n + h), space O(n). With `alpha = 1` the levels equal the data (naive). With `alpha = 0` the level never moves from `y[0]`. Common bugs: starting the level at 0, off-by-one when you forecast (the forecast uses the level **after** the last value), and forgetting the first level in the output.
