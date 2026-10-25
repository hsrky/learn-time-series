---
slug: interpolate-by-time
title: Interpolate by Real Time Distance
difficulty: Medium
type: function
tags: [numpy, interpolation, irregular, from-scratch]
skills: [from-scratch, leakage]
packages: []
companies_style: [IoT sensors]
---
A Series `s` has a sorted `DatetimeIndex` with **unequal** time steps (an [[irregular time series]]). Some values are NaN.

Write `interpolate_by_time(s)`. Fill each NaN **inside** the series with [[linear interpolation]] that uses the real time distance:

`y(t) = y0 + (y1 − y0) · (t − t0) / (t1 − t0)`

where `(t0, y0)` is the last valid point before `t` and `(t1, y1)` is the next valid point after `t`.

NaN values **before the first valid point** or **after the last valid point** stay NaN (no extrapolation). Do not use `Series.interpolate`; write it with numpy.

Remember: this fill uses the future value `y1`. It is fine for describing the past, but not for building inputs of a forecast.

### Example 1
**Input:** times 00:00, 01:00, 04:00; values `[10, NaN, 16]`
**Output:** `[10, 11.5, 16]`
**Explanation:** 01:00 is 1/4 of the way from 00:00 to 04:00. So y = 10 + 6 · 1/4 = 11.5.

### Constraints
- `1 <= len(s) <= 10^5`; the index is sorted and unique.
- Values are floats. There may be no valid point at all (then return all NaN).

### Hints
1. Get the time as numbers: `s.index.asi8` (nanoseconds as integers) or `(s.index - s.index[0]).total_seconds()`.
2. Split the points into valid ones (`~s.isna()`) and the missing ones.
3. `np.interp(x_missing, x_valid, y_valid)` does linear interpolation. It clamps outside the range, so set those positions back to NaN.

### Solution explanation
1. Convert times to floats `x`. Find `ok = s.notna()`.
2. If no valid point exists, return `s` unchanged.
3. `np.interp` at the missing times gives the line values. Positions before `x_valid[0]` or after `x_valid[-1]` are outside, so they stay NaN.

Time O(n log n) or O(n). Bug to avoid: `s.interpolate()` by default uses the row number and ignores the real time distance.
