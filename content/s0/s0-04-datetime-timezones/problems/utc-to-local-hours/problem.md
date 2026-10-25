---
slug: utc-to-local-hours
title: Local Hour of Day from UTC
difficulty: Easy
type: function
tags: [pandas, timezone, datetime]
skills: [pandas-fluency]
packages: []
companies_style: [ride-hailing, retail demand]
---
A server stores event times as text in [[UTC]]. You want to build the feature "hour of day" on the **local clock** of the customers.

Write `local_hours(timestamps, tz)`.

- `timestamps`: a list of strings such as `"2024-07-01 03:10"`. They are UTC and have no zone mark.
- `tz`: a zone name such as `"America/New_York"`.
- Return a list of ints. Item `i` is the local hour (0 to 23) of `timestamps[i]`. Keep the input order.

### Example 1
**Input:** `timestamps = ["2024-07-01 03:10", "2024-07-01 14:05"]`, `tz = "America/New_York"`
**Output:** `[23, 10]`
**Explanation:** In July New York is UTC-4. 03:10 UTC is 23:10 on the day before. 14:05 UTC is 10:05.

### Constraints
- `0 <= len(timestamps) <= 10^5`
- Times may cross a DST change. Use the real zone rules.
- Do not use a Python loop over the timestamps.

### Hints
1. First parse the text with `pd.to_datetime`.
2. The numbers are UTC but have no zone. Which method attaches a zone?
3. `tz_localize("UTC")`, then `tz_convert(tz)`, then `.hour`.

### Solution explanation
1. `idx = pd.to_datetime(timestamps)` makes a naive DatetimeIndex.
2. `idx.tz_localize("UTC")` says the numbers are UTC.
3. `.tz_convert(tz)` changes the clock to the local zone and handles DST.
4. `.hour.tolist()` gives the hours.

Time O(n). Bug to avoid: `tz_localize(tz)` directly would claim that the numbers are already local, so every hour is wrong by the zone offset.
