---
id: s9-06-gaps-and-islands
title: Gaps and islands: consecutive-day streaks
minutes: 30
level: intermediate
goals: [Recognise the gaps-and-islands pattern, Find the longest streak in one pass, Use the day − row number key in pandas]
prereqs: [s9-05-buckets-sessions]
tags: [islands, streaks, pandas]
skills: [streaming-algorithms, pandas-fluency]
---
## Warm-up
```check
{"q": "What does `df['day'].diff()` return for the first row?", "type": "single", "options": ["NaT (missing)", "0", "The first day"], "answer": 0, "why": ["Correct: there is no previous row.", "Not zero; it is missing.", "It is a difference, not a copy."]}
```
```check
{"q": "What does `groupby(key).cumsum()` do when `key` is a user column?", "type": "single", "options": ["A running total inside each user", "One total per user", "Sorts the users"], "answer": 0, "why": ["Correct.", "That is sum().", "It does not sort."]}
```

## Why it matters
Here are three tasks.

- Find the longest [[streak]] of days when a user logged in.
- Find periods when a machine was running without a break.
- Find how many days in a row the temperature was above 30.

All are the **gaps and islands** problem. An **[[island]]** is a block of consecutive items. A **[[gap]]** is a break between islands. It is one of the most common OA patterns, in Python, pandas and SQL.

## The two-step view
Take the login days of one user: 1, 2, 3, 5, 6, 9 (day numbers).

- Islands: {1, 2, 3}, {5, 6}, {9}
- Gaps: between 3 and 5, and between 6 and 9.
- Longest streak: 3 days.

**Method A: one pass.** Sort the unique days. Keep the length of the current run. If `day == previous + 1`, add 1. Otherwise start again at 1. Keep the best length. Time O(n log n) (sort), memory O(1) extra.

**Method B: the key trick.** For days in order, compute `day − row_number`. Inside one island, both grow by 1 every step, so the difference is **constant**. A gap makes the difference jump.

| day | row number | day − row number |
|---|---|---|
| 1 | 1 | 0 |
| 2 | 2 | 0 |
| 3 | 3 | 0 |
| 5 | 4 | 1 |
| 6 | 5 | 1 |
| 9 | 6 | 3 |

Group by the last column and you have the islands. This trick works in pandas (with `rank` or `cumcount`) and in SQL (with `ROW_NUMBER()`).

```chart
{"title": "day − row number is constant inside an island", "x": "row", "height": 200, "series": [{"name": "day", "y": [1, 2, 3, 5, 6, 9], "kind": "dots"}, {"name": "day − row number", "y": [0, 0, 0, 1, 1, 3], "kind": "line"}], "caption": "The group key (orange) only changes where there is a gap."}
```

```check
{"q": "Days 10, 11, 12, 20, 21. What is the key (day − row number, row starts at 1) of the last day?", "type": "numeric", "answer": 16, "tol": 0.01, "why": "The last day is 21 and its row number is 5. 21 − 5 = 16."}
```

## Dates, not numbers
Real data has dates. Convert a date to a day number with `date.toordinal()` in Python. In pandas, use `(d - d.min()).dt.days`, or the equivalent date arithmetic. Then the same trick works. Remember:

- Remove **duplicates** first (two logins on one day).
- **Sort** first.
- For hourly or other steps, divide by the step size.

```check
{"q": "The data has two logins on the same day. What do you do before the trick?", "type": "single", "options": ["Remove duplicate days", "Nothing; the trick handles it", "Sum the logins"], "answer": 0, "why": ["Correct: otherwise the row number increases but the day does not, which breaks the key.", "Duplicates break the constant key.", "Summing is not needed."]}
```

## Worked example
Longest streak in pure Python, and islands in pandas with the trick.

```python
import datetime as dt
import pandas as pd

days = ["2024-03-01", "2024-03-02", "2024-03-02", "2024-03-03", "2024-03-05", "2024-03-06", "2024-03-09"]

# --- pure Python: one pass over the unique, sorted days
nums = sorted({dt.date.fromisoformat(d).toordinal() for d in days})
best = cur = 1
for prev, now in zip(nums, nums[1:]):
    cur = cur + 1 if now == prev + 1 else 1       # continue the run or restart
    best = max(best, cur)
print("longest streak:", best)

# --- pandas: day minus row number gives an island id
s = pd.Series(pd.to_datetime(sorted(set(days))))
key = s - pd.to_timedelta(range(len(s)), unit="D")   # same idea as day - row number
islands = s.groupby(key).agg(["min", "max", "size"]).reset_index(drop=True)
islands["min"] = islands["min"].dt.date          # show dates without the time
islands["max"] = islands["max"].dt.date
print(islands)

# Output:
# longest streak: 3
#           min         max  size
# 0  2024-03-01  2024-03-03     3
# 1  2024-03-05  2024-03-06     2
# 2  2024-03-09  2024-03-09     1
```

## Common mistakes
- Forgetting to remove duplicate days.
- Not sorting before the pass or before `row_number`.
- Mixing users: compute the island key **per user** (`groupby('user')`).
- Using `>= previous + 1` instead of `== previous + 1`.
- Counting the gap length as the number of days between islands, off by one.

## Interview lens
**Typical question:** "Given a user's login dates, find the longest consecutive-day streak."

**Strong answer:** I remove duplicates and sort the dates, then walk once. If a date is exactly one day after the previous, I extend the current run, otherwise I restart at 1. I keep the best run. That is O(n log n) for the sort and O(1) extra space. For many users or for a table, I use the "date minus row number" trick. It gives a constant key inside each consecutive block. I group by it in pandas or SQL. This gives the start, end, and length of every island.

**Red flags:** nested loops (O(n²)); not removing duplicates; ignoring several users.

## Real world
- Retention and "streak" features in consumer apps use exactly this analysis.
- In SQL training material the "gaps and islands" problem is a classic. The `ROW_NUMBER()` trick is documented in many SQL books and blogs.

## Key points
- An island is a block of consecutive items; a gap breaks it.
- One pass: extend the run if `day == previous + 1`.
- Key trick: `day − row_number` is constant inside an island.
- Sort, remove duplicates, and work per user.
