---
slug: login-islands-pandas
title: Login Islands per User (pandas)
difficulty: Medium
type: function
tags: [islands, pandas, groupby]
skills: [pandas-fluency, streaming-algorithms]
packages: []
companies_style: []
---
You get a DataFrame `df` with columns `user` (string) and `day` (datetime64, date only, no time of day). Rows may be in any order and may contain duplicate (user, day) pairs.

Return one row per **island** (a block of consecutive days for one user) with columns `user`, `start`, `end`, `days`, where `days` is the number of distinct days in the island. Sort by `user`, then `start`, and use a clean index.

### Example 1
**Input:** A small log
**Output:** 
```
user      start        end  days
 ann 2024-05-01 2024-05-03     3
 ann 2024-05-05 2024-05-06     2
 bob 2024-05-02 2024-05-02     1
```
**Explanation:** Ann has days 1, 2, 3 and 5 and 6 of May: two islands. Bob has one day.

### Constraints
- 0 <= len(df) <= 10^5

### Hints
1. Remove duplicates with `drop_duplicates()` and sort by user and day.
2. Inside each user, `df.groupby('user').cumcount()` is the row number (starting at 0).
3. `key = day - pd.to_timedelta(row_number, unit='D')` is constant inside an island; group by `[user, key]`.

### Solution explanation
**Approach.** Sort and de-duplicate. Subtract the per-user row number (as days) from each day. This key is constant inside an island. Group by user and key and take the minimum, maximum and size.

**Why it works.** Inside an island both the day and the row number grow by one each step, so their difference stays constant. A gap makes the day jump but the row number grows by one, so the key changes.

**Complexity.** O(n log n) for sorting; the rest is O(n). Memory O(n).

**Common bugs.** Not removing duplicates; computing the row number globally instead of per user; forgetting to reset the index.
