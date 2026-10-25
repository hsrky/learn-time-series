---
slug: sql-fill-missing-dates
title: Fill Missing Dates with a Recursive CTE
difficulty: Medium
type: sql
tags: [sql, recursive-cte, calendar]
skills: [sql-time-series]
packages: []
companies_style: []
---
Table `daily(day TEXT, revenue REAL)` has no rows for days without sales. `day` has the form `YYYY-MM-DD`; each day appears at most once and the table has at least one row.

Return **every calendar day** from the first to the last day in the table with columns `day` and `revenue`. Days without a row get revenue `0`. Order by `day`.

Hint: `date(day, '+1 day')` adds one day in sqlite.

### Example 1
**Input:** Table `daily`:
```
       day  revenue
2024-01-01     10.0
2024-01-02     20.0
2024-01-05     50.0
```

**Output:** 
```
       day  revenue
2024-01-01     10.0
2024-01-02     20.0
2024-01-03      0.0
2024-01-04      0.0
2024-01-05     50.0
```
**Explanation:** The days 01-03 and 01-04 are missing in the table, so they appear with revenue 0.

### Constraints
- 1 <= rows <= 5000

### Hints
1. Build a calendar with `WITH RECURSIVE cal(day) AS (SELECT MIN(day) FROM daily UNION ALL SELECT date(day, '+1 day') FROM cal WHERE day < (SELECT MAX(day) FROM daily))`.
2. `LEFT JOIN daily` on the day so that every calendar day stays.
3. `COALESCE(revenue, 0)` replaces the missing values.

### Solution explanation
**Approach.** Generate all days with a recursive CTE (anchor = first day, step = next day, stop at the last day). Left join the sales on the day and replace NULL by 0.

**Why it works.** The calendar has exactly one row per day. The left join keeps all calendar rows and adds the revenue where it exists.

**Complexity.** The calendar has D rows (D = number of days from first to last). The join costs O(D log n) with an index or O(D + n) with a hash join. Space O(D).

**Common bugs.** Missing stop condition (endless recursion); inner join instead of left join; filling NULL with 0 in a case where 0 is wrong (here the task says 0).
