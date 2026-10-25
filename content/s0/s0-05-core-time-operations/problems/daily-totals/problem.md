---
slug: daily-totals
title: Daily Totals from Hourly Data
difficulty: Easy
type: function
tags: [pandas, resample]
skills: [pandas-fluency]
packages: []
companies_style: [energy, retail demand]
---
You have a Series `s` of hourly electricity use (kWh) with a `DatetimeIndex`. Some hours can be missing (NaN).

Write `daily_totals(s)`. Return a Series with the **total per calendar day**. Each day appears, also days where all hours are missing. Missing hours count as 0 in the total.

### Example 1
**Input:** `s` has 48 hourly values, all equal to 1.0, starting at 2024-01-01 00:00
**Output:** a Series: 2024-01-01 → 24.0, 2024-01-02 → 24.0
**Explanation:** Each day has 24 hours of 1.0 kWh.

### Constraints
- `s` has a `DatetimeIndex` and is sorted.
- Calendar days are in the index's own clock (no time zone change needed).
- Gaps in the index are possible. A day with no rows at all must still appear with total 0.0 if it lies between the first and last day.

### Hints
1. The tool that changes frequency is `resample`.
2. `s.resample("D")` groups rows by calendar day. Which aggregation gives a total?
3. `sum()` skips NaN by default and returns 0.0 for an empty or all-NaN day. That is exactly what you need.

### Solution explanation
1. `s.resample("D").sum()` makes one row per day from the first to the last day.
2. For days without data, the sum of nothing is 0.0 (the default `min_count=0`).

Time O(n). Bug to avoid: `.mean()` gives the average hour, not the total.
