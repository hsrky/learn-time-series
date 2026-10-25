---
slug: missing-timestamps
title: Find the Missing Timestamps
difficulty: Easy
type: function
tags: [pandas, datetime, data-quality]
skills: [pandas-fluency]
packages: []
companies_style: [IoT sensors, data quality]
---
A sensor should send one reading at every step of a fixed frequency. Some readings did not arrive.

Write `missing_timestamps(index, freq)`.

- `index`: a `DatetimeIndex` of the times that **did** arrive. It can be unsorted and can contain duplicates.
- `freq`: a pandas frequency code such as `"h"` or `"D"`.
- Return a list of strings `"YYYY-MM-DD HH:MM"` with the missing times, sorted from oldest to newest. Only look between the first and the last time in `index`.

### Example 1
**Input:** `index = ["2024-01-01 00:00", "2024-01-01 01:00", "2024-01-01 04:00"]`, `freq = "h"`
**Output:** `["2024-01-01 02:00", "2024-01-01 03:00"]`
**Explanation:** The full hourly calendar from 00:00 to 04:00 has 5 steps. Two of them are not in the index.

### Constraints
- `0 <= len(index) <= 10^5`
- Return `[]` for an empty index or when nothing is missing.
- Times in `index` are on the grid of `freq` (for example, whole hours for `"h"`).

### Hints
1. Build the full calendar with `pd.date_range(start, end, freq=freq)`.
2. Which `Index` method gives the elements of one index that are not in another?
3. `full.difference(index)` is sorted. Format it with `.strftime("%Y-%m-%d %H:%M")`.

### Solution explanation
1. If the index is empty, return `[]`.
2. `full = pd.date_range(index.min(), index.max(), freq=freq)` is the complete calendar.
3. `full.difference(index)` removes every time that arrived. It ignores duplicates and order.
4. Format the result as strings.

Time O(n + m) for a calendar of m steps. Bug to avoid: comparing only the *number* of rows with the expected number does not tell you *which* times are missing.
