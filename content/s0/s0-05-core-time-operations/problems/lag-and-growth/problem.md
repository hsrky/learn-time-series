---
slug: lag-and-growth
title: Lag, Change and Growth Table
difficulty: Easy
type: function
tags: [pandas, shift, diff, pct_change]
skills: [pandas-fluency, leakage]
packages: []
companies_style: [e-commerce]
---
A Series `s` holds daily sales. Write `lag_table(s)`. It returns a DataFrame with the same index as `s` and these columns in this order:

| column | meaning |
|---|---|
| `sales` | the original values |
| `lag1` | the value of the previous row |
| `change` | `sales` minus `lag1` |
| `growth` | `change` divided by `lag1` |
| `avg3_before` | the mean of the **three previous** rows (not today). It is NaN until three previous rows exist. |

### Example 1
**Input:** `s = [10, 20, 40, 40]` (4 days)
**Output:**

| sales | lag1 | change | growth | avg3_before |
|---|---|---|---|---|
| 10 | NaN | NaN | NaN | NaN |
| 20 | 10 | 10 | 1.0 | NaN |
| 40 | 20 | 20 | 1.0 | NaN |
| 40 | 40 | 0 | 0.0 | 23.333… |

**Explanation:** The last `avg3_before` is the mean of 10, 20 and 40. Today's 40 is not used.

### Constraints
- `1 <= len(s) <= 10^5`; values are positive floats or ints.
- Do not use a Python loop.

### Hints
1. `s.shift(1)` gives the previous value.
2. `s.diff()` or `s - lag1` gives the change. `s.pct_change()` gives the growth.
3. For `avg3_before`, compute the rolling mean of 3 first and then `shift(1)`, so that today is outside the window.

### Solution explanation
1. `lag1 = s.shift(1)`.
2. `change = s - lag1`; `growth = change / lag1`.
3. `avg3_before = s.rolling(3).mean().shift(1)`. The window at row t covers rows t−3 to t−1 after the shift.

Time O(n). Bug to avoid: `s.rolling(3).mean()` without shift includes today, which is leakage.
