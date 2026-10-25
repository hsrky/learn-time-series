---
slug: sql-day-over-day
title: Day-over-Day Change (LAG and LEAD)
difficulty: Easy
type: sql
tags: [sql, window-functions, lag]
skills: [sql-time-series]
packages: []
companies_style: []
---
Table `daily(day TEXT, revenue REAL)` has one row per day, with `day` in `YYYY-MM-DD` form.

Write a query that returns, for every day, these columns in this order: `day`, `revenue`, `prev_revenue` (the revenue of the previous row), `next_revenue` (the revenue of the next row) and `change` (`revenue - prev_revenue`). The first and last rows have `NULL` where a neighbour is missing. Order the result by `day`.

Edit the `QUERY` string. The table is passed in as `daily`.

### Example 1
**Input:** Table `daily`:
```
       day  revenue
2024-01-01    100.0
2024-01-02    130.0
2024-01-03    120.0
```

**Output:** 
```
       day  revenue  prev_revenue  next_revenue  change
2024-01-01    100.0           NaN         130.0     NaN
2024-01-02    130.0         100.0         120.0    30.0
2024-01-03    120.0         130.0           NaN   -10.0
```
**Explanation:** The first row has no previous day; the last row has no next day.

### Constraints
- 1 <= rows <= 10^5
- Each day appears once

### Hints
1. `LAG(revenue) OVER (ORDER BY day)` is the previous revenue.
2. `LEAD(revenue) OVER (ORDER BY day)` is the next revenue.
3. Compute `change` as `revenue - LAG(revenue) OVER (ORDER BY day)` and finish with `ORDER BY day`.

### Solution explanation
**Approach.** One query with three window functions that share the same ordering by `day`. No self-join is needed.

**Why it works.** Window functions look at neighbouring rows in the order given inside `OVER`. The edge rows have no neighbour, so `NULL` is returned.

**Complexity.** The database sorts once: O(n log n) time and O(n) space. With an index on `day` it can be O(n).

**Common bugs.** Missing `ORDER BY` inside `OVER`; computing the change with a self-join on `day - 1` (breaks at month ends if you do text arithmetic); forgetting the final `ORDER BY`.
