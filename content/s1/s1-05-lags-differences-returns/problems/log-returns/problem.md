---
slug: log-returns
title: Log Returns
difficulty: Easy
type: function
tags: [pandas, numpy, returns, log]
skills: [pandas-fluency, from-scratch]
packages: []
companies_style: [finance, pricing]
---
A Series `prices` holds positive prices with a `DatetimeIndex`. Write `log_returns(prices)`. It returns a Series with the same index. The value at time t is `ln(p(t) / p(t−1))`. The first value is `NaN` because there is no previous price.

### Example 1
**Input:** `prices = [100, 110, 99]`
**Output:** `[NaN, 0.0953, -0.1054]` (rounded)
**Explanation:** ln(110/100) = 0.0953 and ln(99/110) = −0.1054.

### Constraints
- `1 <= len(prices) <= 10^5`; every price is greater than 0.
- Use vectorized code. No Python loop.

### Hints
1. The previous price is `prices.shift(1)`.
2. Divide the prices by the previous prices.
3. Apply `np.log` to the ratio. (A second way: `np.log(prices).diff()`.)

### Solution explanation
1. `np.log(prices / prices.shift(1))` computes the log of each ratio. The first ratio is NaN, so the first result is NaN.
2. The two ways are equal because ln(a/b) = ln a − ln b.

Time O(n). Bug to avoid: `prices.pct_change()` is the *simple* return, which is a different number.
