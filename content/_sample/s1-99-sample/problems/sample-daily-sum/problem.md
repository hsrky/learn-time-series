---
slug: sample-daily-sum
title: Daily Totals from Hourly Data
difficulty: Easy
type: function
tags: [pandas, resample]
skills: [pandas-fluency]
packages: []
---
Return the **daily total** of an hourly series.

### Example 1
**Input:** `s` with 48 hourly values
**Output:** a Series with 2 values

### Constraints
- The index is a `DatetimeIndex`.

### Hints
1. Think about resampling.
2. Use `resample("D")`.
3. Call `.sum()`.

### Solution explanation
Resample to days and sum. O(n).
