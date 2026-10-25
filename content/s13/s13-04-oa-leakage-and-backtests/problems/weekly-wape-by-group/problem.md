---
slug: weekly-wape-by-group
title: Weekly WAPE by Group
difficulty: Medium
type: function
tags: [pandas, metrics, WAPE, groupby, weekly]
skills: [metrics, pandas-fluency]
packages: []
companies_style: [retail demand, forecast reporting]
---
Your team reports forecast quality every week. The table has one row per group and day with the real value `actual` and the forecast `forecast`.

WAPE (weighted absolute percentage error) for a set of rows is:

`WAPE = sum(|actual - forecast|) / sum(actual)`

Write `weekly_wape(df)`. Weeks start on **Monday**. For each group and each week that has at least one row, compute WAPE using all rows of that group in that week. If `sum(actual)` is 0 for that group-week, the WAPE is `NaN`.

`df` has columns `group`, `date` (datetime, may include a time of day), `actual`, `forecast`. Return a DataFrame with columns `group`, `week_start` (the Monday, at midnight), `wape`, sorted by `group` then `week_start`, with a fresh index.

### Example 1
**Input:**
```
group  date        actual  forecast
A      2024-01-01  100     90        (Monday)
A      2024-01-03  100     120       (Wednesday)
A      2024-01-08  50      50        (next Monday)
```
**Output:**
```
group  week_start  wape
A      2024-01-01  0.15
A      2024-01-08  0.00
```
**Explanation:** Week 1: errors 10 + 20 = 30, actual sum 200, so 0.15. Week 2: error 0.

### Constraints
- 0 ≤ number of rows ≤ 10^5
- `actual` ≥ 0
- A week with no rows for a group is not in the output

### Hints
1. Find the Monday of each date: `date.dt.normalize() - pd.to_timedelta(date.dt.weekday, unit="D")`.
2. Add a column with the absolute error. Then `groupby(["group", "week_start"])` and sum the error and the actual.
3. Divide the two sums. Where the actual sum is 0, return NaN (use `where`).

### Solution explanation
Compute the week start for each row. Sum absolute error and actual per group and week, then divide. Do **not** average the daily percentage errors: WAPE is a ratio of sums. Division by 0 gives `inf` or NaN, so we replace it by NaN. Time O(n log n). Common bugs: using `resample("W")` (it ends weeks on Sunday and labels them by the end date), averaging daily APE, and forgetting the time of day when finding the Monday.
