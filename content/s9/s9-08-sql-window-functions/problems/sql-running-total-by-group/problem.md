---
slug: sql-running-total-by-group
title: Running Total per Store
difficulty: Medium
type: sql
tags: [sql, window-functions, partition]
skills: [sql-time-series]
packages: []
companies_style: []
---
Table `orders(store TEXT, day TEXT, amount REAL)` has one row per order. A store can have **several orders on the same day**.

Return `store`, `day`, `amount` and `running_total`: the sum of `amount` over all rows of the same store up to and including the current row. Rows of a store are ordered by `day`; rows of the same store and day are ordered by `amount` (small first). Order the final result by `store`, `day`, `amount`.

The running total must add one row at a time, so two orders on the same day get **different** totals.

### Example 1
**Input:** Table `orders`:
```
store        day  amount
    A 2024-01-01    10.0
    A 2024-01-02     5.0
    A 2024-01-02     7.0
    B 2024-01-01   100.0
    B 2024-01-03     1.0
```

**Output:** 
```
store        day  amount  running_total
    A 2024-01-01    10.0           10.0
    A 2024-01-02     5.0           15.0
    A 2024-01-02     7.0           22.0
    B 2024-01-01   100.0          100.0
    B 2024-01-03     1.0          101.0
```
**Explanation:** Store A has two orders on 2024-01-02. Each row gets its own running total, because we count rows, not days.

### Constraints
- 1 <= rows <= 10^5

### Hints
1. `SUM(amount) OVER (PARTITION BY store ORDER BY day, amount ...)`.
2. Write the frame: `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`.
3. Without `ROWS`, rows with the same order values would share one total.

### Solution explanation
**Approach.** A windowed `SUM` partitioned by store and ordered by day and amount, with an explicit `ROWS` frame from the start to the current row.

**Why it works.** `PARTITION BY` restarts the sum for every store. The `ROWS` frame adds one row at a time, so ties get separate totals.

**Complexity.** O(n log n) for sorting, O(n) for the running sum. Space O(n).

**Common bugs.** Using `GROUP BY` (collapses rows); no `PARTITION BY` (one total for all stores); the default `RANGE` frame; missing final `ORDER BY`.
