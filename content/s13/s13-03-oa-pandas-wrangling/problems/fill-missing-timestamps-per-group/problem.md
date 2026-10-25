---
slug: fill-missing-timestamps-per-group
title: Fill Missing Days per Store
difficulty: Easy
type: function
tags: [pandas, reindex, groupby, missing-data]
skills: [pandas-fluency]
packages: []
companies_style: [retail demand, OA warm-up]
---
A table has daily sales for several stores. Some days are missing: the store has no row for that day.

Write `fill_missing_days(df)`. For each store, add a row for every missing calendar day between the store's **first** and **last** date. Set `sales` to `0` on the new rows.

The input has columns `store`, `date` (datetime, one row per store and day at most) and `sales`. The rows can be in any order.

Return a DataFrame with the same three columns, sorted by `store` and then `date`, with a fresh index `0, 1, 2, ...`. Do not add days before a store's first date or after its last date.

### Example 1
**Input:**
```
store  date        sales
A      2024-01-01  5
A      2024-01-04  7
B      2024-01-02  3
```
**Output:**
```
store  date        sales
A      2024-01-01  5
A      2024-01-02  0
A      2024-01-03  0
A      2024-01-04  7
B      2024-01-02  3
```
**Explanation:** Store A misses January 2 and 3, so two rows with 0 are added. Store B has one date only, so nothing is added.

### Constraints
- 0 ≤ number of rows ≤ 10^5
- Each (store, date) pair appears at most once
- Dates are daily; times of day are always midnight

### Hints
1. Handle each store on its own. `groupby("store")` gives you one block per store.
2. For one store, build the full range with `pd.date_range(first, last, freq="D")`.
3. Put `date` in the index and call `reindex(full_range, fill_value=0)`. Then rebuild the columns.

### Solution explanation
Group by store. In each group, set `date` as the index and reindex to a full daily range between that group's minimum and maximum. `fill_value=0` writes 0 for the new days only. Stack the pieces and sort.

Time is O(n log n) because of sorting. A common bug is to build one global date range for all stores. That adds days before a store opened. Another bug is to use `resample("D").asfreq()` and forget to fill the new rows with 0 instead of NaN.
