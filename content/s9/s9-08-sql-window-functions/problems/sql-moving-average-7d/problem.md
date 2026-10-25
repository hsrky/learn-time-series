---
slug: sql-moving-average-7d
title: 7-Day Moving Average in SQL
difficulty: Medium
type: sql
tags: [sql, window-functions, moving-average]
skills: [sql-time-series]
packages: []
companies_style: []
---
Table `daily(day TEXT, revenue REAL)` has one row per calendar day.

Return `day`, `revenue` and `avg_7d`, the average revenue of the current day and the 6 days before it, **rounded to 2 decimals**. For the first 6 days (when fewer than 7 rows exist) `avg_7d` must be `NULL`. Order by `day`.

### Example 1
**Input:** Table `daily`:
```
       day  revenue
2024-03-01     10.0
2024-03-02     20.0
2024-03-03     30.0
2024-03-04     40.0
2024-03-05     50.0
2024-03-06     60.0
2024-03-07     70.0
2024-03-08    150.0
```

**Output:** 
```
       day  revenue  avg_7d
2024-03-01     10.0     NaN
2024-03-02     20.0     NaN
2024-03-03     30.0     NaN
2024-03-04     40.0     NaN
2024-03-05     50.0     NaN
2024-03-06     60.0     NaN
2024-03-07     70.0    40.0
2024-03-08    150.0    60.0
```
**Explanation:** The first six rows have no full week. From day 7 on, the average covers 7 days.

### Constraints
- 1 <= rows <= 10^5
- Each day appears once and there are no missing days

### Hints
1. `AVG(revenue) OVER (ORDER BY day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)` is the average.
2. `COUNT(*) OVER (the same frame)` tells you how many rows are in the frame.
3. Use `CASE WHEN COUNT(*) OVER (...) = 7 THEN ROUND(AVG(...) OVER (...), 2) END`.

### Solution explanation
**Approach.** One window frame of 7 rows (6 before plus the current one). A `CASE` checks that the frame is full, so early rows give `NULL`, like `rolling(7).mean()` in pandas.

**Why it works.** `ROWS` counts physical rows, so with exactly one row per day it is a calendar-week window.

**Complexity.** O(n log n) for the sort, then O(n) for the frame (databases keep a running sum). Space O(n).

**Common bugs.** `7 PRECEDING` (8 rows); using `RANGE`; forgetting to round; returning a partial average for the first 6 days; missing days (rows are not days).
