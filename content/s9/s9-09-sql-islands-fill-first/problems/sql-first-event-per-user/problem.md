---
slug: sql-first-event-per-user
title: First Event per User
difficulty: Medium
type: sql
tags: [sql, row-number, partition]
skills: [sql-time-series]
packages: []
companies_style: []
---
Table `events(event_id INTEGER, user_id TEXT, event_time TEXT, event_type TEXT)` has one row per event. `event_time` has the form `YYYY-MM-DD HH:MM:SS`. `event_id` is unique.

Return the **first event of each user**: columns `user_id`, `event_id`, `event_type`, `event_time`. If a user has two events at the same time, choose the one with the smaller `event_id`. Order by `user_id`.

### Example 1
**Input:** Table `events`:
```
 event_id user_id          event_time event_type
        1      u1 2024-05-01 09:30:00      click
        2      u2 2024-05-01 08:00:00      login
        3      u1 2024-05-01 09:00:00      login
        4      u1 2024-05-02 10:00:00        buy
        5      u1 2024-05-01 09:00:00       view
```

**Output:** 
```
user_id  event_id event_type          event_time
     u1         3      login 2024-05-01 09:00:00
     u2         2      login 2024-05-01 08:00:00
```
**Explanation:** User u1 has two events at 09:00:00 (ids 3 and 5); the smaller id wins.

### Constraints
- 1 <= rows <= 10^5

### Hints
1. `ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY event_time, event_id)` numbers the events of each user.
2. Put it in a sub-query or CTE and keep `rn = 1`.
3. Select the columns in the order of the statement.

### Solution explanation
**Approach.** Number each user's events by time (and id as tie-breaker) and keep the row with number 1.

**Why it works.** `PARTITION BY` creates one list per user and `ORDER BY` puts the earliest event first. The tie-breaker makes the choice unique.

**Complexity.** One sort per partition: O(n log n) total time, O(n) space.

**Common bugs.** `GROUP BY user_id` with `MIN(event_time)` loses the other columns; `LIMIT 1` returns one row in total; no tie-breaker gives unstable results.
