---
slug: causal-fill
title: Clean and Fill Without Looking Ahead
difficulty: Medium
type: function
tags: [pandas, missing-data, ffill, leakage]
skills: [leakage, pandas-fluency]
packages: []
companies_style: [IoT sensors, energy]
---
A sensor sends one temperature per day, but the log has problems:

- Some days have **no row**.
- The value `-999` means "sensor failed" (a hidden missing value).
- Some values are NaN.

Write `causal_fill(s, max_gap)`. Return a clean daily Series:

1. Replace `-999` by NaN.
2. Put the series on a **full daily grid** from its first date to its last date.
3. Fill missing values with the last known value, but for **at most `max_gap` days in a row**. Longer gaps stay NaN after the first `max_gap` filled days.

Never use a later value to fill an earlier day.

### Example 1
**Input:** `s` on 1, 2, 5, 6 January = `[10, -999, 14, 15]`, `max_gap = 1`
**Output:** `[10, 10, NaN, NaN, 14, 15]` for 1 to 6 January
**Explanation:** The -999 becomes NaN. The grid has 6 days because 3 and 4 January are new rows. With `max_gap = 1` only one day after a known value is filled: 2 January gets 10. The days 3 and 4 January stay NaN.

### Constraints
- `1 <= len(s) <= 10^5`; the index is a sorted `DatetimeIndex` of whole days.
- `max_gap >= 0`. With `max_gap = 0` nothing is filled.

### Hints
1. `s.replace(-999, np.nan)` handles the hidden missing value.
2. `s.reindex(pd.date_range(first, last, freq="D"))` adds the missing rows.
3. `Series.ffill(limit=...)` copies forward for a limited number of steps.

### Solution explanation
1. Replace the code, then reindex to the daily grid.
2. `ffill(limit=max_gap)` fills only the first `max_gap` NaN after each known value. It uses only past values, so there is no leakage.

Time O(n + d). Bug to avoid: `interpolate()` or `bfill()` would use a later value. Another bug: calling `ffill` before the reindex leaves the missing rows unfilled.
