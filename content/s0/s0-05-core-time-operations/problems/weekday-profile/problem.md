---
slug: weekday-profile
title: Weekday Profile
difficulty: Easy
type: function
tags: [pandas, groupby, seasonality]
skills: [pandas-fluency]
packages: []
companies_style: [retail demand, web traffic]
---
A Series `s` holds daily sales with a `DatetimeIndex`. You want the **weekly shape**: the average sales for each day of the week.

Write `weekday_profile(s)`. Return a Series with 7 values, indexed `0` (Monday) to `6` (Sunday). Each value is the mean of `s` over all dates with that weekday. If a weekday never occurs in `s`, its value is `NaN`. The result must always have all 7 labels, in order.

### Example 1
**Input:** `s` has 14 days from Monday 2024-01-01 with values 1, 2, 3, 4, 5, 6, 7, 3, 4, 5, 6, 7, 8, 9
**Output:** index 0..6 with values 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0
**Explanation:** Monday has 1 and 3, mean 2. Tuesday has 2 and 4, mean 3. And so on.

### Constraints
- `1 <= len(s) <= 10^5`; the index is a `DatetimeIndex`.
- NaN values are skipped in the mean.

### Hints
1. The weekday number of each date is `s.index.dayofweek`.
2. Group by it: `s.groupby(...)`, then take the mean.
3. If a weekday is missing, use `reindex(range(7))` so that the result still has 7 rows.

### Solution explanation
1. `s.groupby(s.index.dayofweek).mean()` averages all rows with the same weekday.
2. `.reindex(range(7))` makes sure all 7 weekdays appear, in order, with NaN for any missing one.

Time O(n). Bug to avoid: `resample("W")` gives one value per week, not per weekday.
