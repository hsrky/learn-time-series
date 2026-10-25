---
slug: sql-login-islands
title: Login Streaks in SQL (Gaps and Islands)
difficulty: Hard
type: sql
tags: [sql, gaps-and-islands, row-number]
skills: [sql-time-series]
packages: []
companies_style: []
---
Table `logins(user_id TEXT, day TEXT)` stores one row per login. `day` has the form `YYYY-MM-DD`. A user can log in several times on one day.

Return one row per **island** (a block of consecutive days for one user): `user_id`, `start_day`, `end_day`, `days` (number of distinct days). Order by `user_id`, then `start_day`.

Hint: in sqlite, `date(day, '-' || rn || ' day')` subtracts `rn` days from a date text.

### Example 1
**Input:** Table `logins`:
```
user_id        day
      a 2024-01-01
      a 2024-01-02
      a 2024-01-02
      a 2024-01-03
      a 2024-01-05
      b 2024-01-10
```

**Output:** 
```
user_id  start_day    end_day  days
      a 2024-01-01 2024-01-03     3
      a 2024-01-05 2024-01-05     1
      b 2024-01-10 2024-01-10     1
```
**Explanation:** User a has the island 01-01 to 01-03 (the duplicate login on 01-02 is counted once) and the island 01-05. User b has one island.

### Constraints
- 1 <= rows <= 10^5

### Hints
1. First get distinct (user_id, day) pairs.
2. `ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY day)` numbers the days of each user.
3. `GROUP BY user_id, date(day, '-' || rn || ' day')` groups the days of one island.

### Solution explanation
**Approach.** Remove duplicates, number the days per user, compute the island key (date minus row number), and group by user and key.

**Why it works.** Inside an island, the date and the row number both grow by one, so their difference does not change. A gap makes the date jump, so the key changes.

**Complexity.** One sort for the window function: O(n log n) time, O(n) space.

**Common bugs.** No `DISTINCT` (duplicates break the key); `ROW_NUMBER` without `PARTITION BY`; forgetting that `rn` must be turned into a text like `'-3 day'`.
