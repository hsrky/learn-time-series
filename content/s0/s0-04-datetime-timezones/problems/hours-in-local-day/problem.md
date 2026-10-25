---
slug: hours-in-local-day
title: How Long Is This Local Day?
difficulty: Easy
type: function
tags: [pandas, timezone, dst]
skills: [pandas-fluency]
packages: []
companies_style: [energy, retail demand]
---
Daily totals of hourly data look odd on days when clocks change, because the local day is not 24 hours long.

Write `hours_in_day(date, tz)`. It returns the number of real hours in the local calendar day `date` (a string `"YYYY-MM-DD"`) in the zone `tz`. The answer is 23, 24 or 25.

### Example 1
**Input:** `date = "2024-03-10"`, `tz = "America/New_York"`
**Output:** `23`
**Explanation:** The clocks jump forward on this day. One hour (02:00) does not exist.

### Example 2
**Input:** `date = "2024-03-11"`, `tz = "America/New_York"`
**Output:** `24`

### Constraints
- Use dates and zones where local midnight always exists (such as the USA, Europe, Asia, Australia/Sydney).
- Return an int.

### Hints
1. A local day starts at local midnight and ends at the next local midnight.
2. Make two aware Timestamps: midnight of `date` and midnight of the next day, both in `tz`.
3. Subtract them and convert the Timedelta to hours: `.total_seconds() / 3600`.

### Solution explanation
1. `start = pd.Timestamp(date).tz_localize(tz)` is local midnight.
2. `end = (pd.Timestamp(date) + pd.Timedelta(days=1)).tz_localize(tz)` is the next local midnight.
3. `end - start` is a real elapsed time, so DST is counted. Divide the seconds by 3600.

Time O(1). Bug to avoid: adding `pd.Timedelta(hours=24)` to the *aware* start gives a moment 24 real hours later, which is wrong on DST days. Add the day to the naive date, then localize.
