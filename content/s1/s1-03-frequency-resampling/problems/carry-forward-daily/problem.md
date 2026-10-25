---
slug: carry-forward-daily
title: Daily Price From Change Dates
difficulty: Easy
type: function
tags: [pandas, upsampling, ffill, leakage]
skills: [pandas-fluency, leakage]
packages: []
companies_style: [retail pricing]
---
A shop saves its price only on the days when the price **changes**. The Series `changes` has those dates as index and the new price as value. The index may be unsorted.

Write `daily_price(changes, end)`. Return a daily Series from the first change date until `end` (a date string, included). Each day gets the **most recent price that was set on or before that day**. Do not use any later price.

### Example 1
**Input:** `changes = {2024-01-01: 5.0, 2024-01-04: 6.0}`, `end = "2024-01-06"`
**Output:** 2024-01-01 → 5, 01-02 → 5, 01-03 → 5, 01-04 → 6, 01-05 → 6, 01-06 → 6
**Explanation:** The price 6.0 starts on 4 January. Earlier days keep 5.0.

### Constraints
- `1 <= len(changes) <= 10^4`; dates have no time of day.
- `end` is on or after the first change date. Change dates after `end` are ignored.
- Never use `bfill` or `interpolate`: they would use a future price.

### Hints
1. Sort the index first.
2. Make the full daily calendar with `pd.date_range`.
3. `reindex(calendar, method="ffill")` copies the last known value forward.

### Solution explanation
1. `changes = changes.sort_index()`.
2. `calendar = pd.date_range(changes.index[0], end, freq="D")`.
3. `changes.reindex(calendar, method="ffill")` gives each day the latest value at or before that day. It looks only into the past, so there is no leakage.

Time O(n + d) for d days. Bug to avoid: `interpolate()` would invent prices between two change dates and uses the future one.
