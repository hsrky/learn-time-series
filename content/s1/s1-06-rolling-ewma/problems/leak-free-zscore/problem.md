---
slug: leak-free-zscore
title: Leak-free Rolling Z-score
difficulty: Medium
type: function
tags: [pandas, rolling, z-score, leakage, anomaly]
skills: [leakage, pandas-fluency]
packages: []
companies_style: [monitoring, anomaly detection]
---
To find strange values in a metric, we compare each value with the recent past. Write `rolling_zscore(s, window)`.

For each time t, return

`z(t) = (s[t] − mean) / std`

where `mean` and `std` are computed from the **`window` values before t** (rows t−window to t−1). The value `s[t]` itself is **not** in the window.

- Use the sample standard deviation (`ddof=1`, the pandas default).
- `z(t)` is NaN when fewer than `window` previous values exist.
- `z(t)` is NaN when `std` is 0 (all previous values are equal).

### Example 1
**Input:** `s = [10, 12, 14, 30]`, `window = 3`
**Output:** `[NaN, NaN, NaN, 9.0]`
**Explanation:** For the last value the previous three are 10, 12, 14: mean 12, std 2. So z = (30 − 12) / 2 = 9.

### Constraints
- `1 <= len(s) <= 10^5`; `window >= 2`.
- Do not use a Python loop. A rolling window that includes `s[t]` is wrong.

### Hints
1. Shift the series by one: `past = s.shift(1)`. Now row t holds `s[t−1]`.
2. `past.rolling(window)` windows now end at t−1.
3. Compute `mean` and `std` from that, then `(s − mean) / std`. Replace infinite values (std = 0) by NaN.

### Solution explanation
1. `past = s.shift(1)` moves everything one step later, so a window ending at row t covers t−window to t−1.
2. `mean = past.rolling(window).mean()` and `std = past.rolling(window).std()`.
3. `z = (s − mean) / std`. Division by 0 gives inf or NaN. We set std = 0 to NaN before dividing.

Time O(n). Bug to avoid: `s.rolling(window).mean()` includes today's value, which pulls the mean toward the value and hides the anomaly.
