---
slug: sessionize-pandas
title: Sessionize Events (pandas)
difficulty: Medium
type: function
tags: [sessions, pandas, groupby, cumsum]
skills: [pandas-fluency, streaming-algorithms]
packages: []
companies_style: []
---
You get a DataFrame `df` with columns `user` (string) and `ts` (datetime64). Rows are in any order.

Start a new session when the gap to the user's previous event is **more than 30 minutes**. Return a DataFrame with one row per session and these columns in this order:

`user`, `session` (1, 2, 3, ... inside each user), `start` (first `ts`), `end` (last `ts`), `events` (number of rows).

Sort the result by `user`, then `session`, and give it a clean index (0, 1, 2, ...). Do not change the input DataFrame.

### Example 1
**Input:** A small log of two users
**Output:** 
```
user  session               start                 end  events
 ann        1 2024-05-01 09:00:00 2024-05-01 09:10:00       2
 ann        2 2024-05-01 10:00:00 2024-05-01 10:00:00       1
 bob        1 2024-05-01 09:05:00 2024-05-01 09:05:00       1
```
**Explanation:** Ann's events at 09:00, 09:10 and 10:00 form two sessions (the last gap is 50 minutes). Bob has one session.

### Constraints
- 0 <= len(df) <= 10^5
- ts has no missing values

### Hints
1. `df.sort_values(['user', 'ts'])` first.
2. `gap = df.groupby('user')['ts'].diff()`; a session starts where `gap` is NaT or larger than `pd.Timedelta(minutes=30)`.
3. `flag.groupby(df['user']).cumsum()` gives the session number; then `groupby([...]).agg(...)`.

### Solution explanation
**Approach.** Sort, compute the per-user gap, flag session starts, number the sessions with a cumulative sum per user, then aggregate start, end and count.

**Why it works.** The flag is 1 exactly at the first event of each session, so the running total increases by one per session.

**Complexity.** O(n log n) for the sort; the other steps are O(n). Memory O(n).

**Common bugs.** Forgetting `groupby('user')` in `diff` or in `cumsum`; comparing a timedelta with an integer; changing the input in place; wrong column order.
