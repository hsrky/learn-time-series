---
id: s9-09-sql-islands-fill-first
title: SQL: islands, missing dates and first event
minutes: 35
level: intermediate
goals: [Solve gaps and islands in SQL, Fill missing dates with a recursive CTE, Get the first event per user]
prereqs: [s9-08-sql-window-functions, s9-06-gaps-and-islands]
tags: [sql, islands, recursive-cte]
skills: [sql-time-series]
---
## Warm-up
```check
{"q": "What does ROW_NUMBER() OVER (PARTITION BY user ORDER BY ts) return?", "type": "single", "options": ["1, 2, 3, ... for the rows of each user in time order", "The total number of rows", "The row id in the file"], "answer": 0, "why": ["Correct.", "That is COUNT(*).", "It is a computed number, not a file id."]}
```
```check
{"q": "Which tool in SQL repeats a query step until a condition stops it?", "type": "single", "options": ["WITH RECURSIVE", "GROUP BY", "UNION ALL alone"], "answer": 0, "why": ["Correct: a recursive common table expression.", "GROUP BY does not repeat.", "UNION ALL is used inside the recursion, but alone it does not repeat."]}
```

## Why it matters
Three more OA favourites in SQL:

1. "Find each user's **streaks** of consecutive days." (gaps and islands)
2. "Show revenue for **every** day, with 0 for days without sales." (fill missing dates)
3. "Return the **first** event of each user." (first per group)

Each has a standard pattern. If you know the pattern, you write the query in two minutes.

## Gaps and islands in SQL
Remember the Python trick: `day − row_number` is constant inside an [[island]]. In SQL:

```sql
WITH d AS (
  SELECT DISTINCT user_id, day FROM logins           -- remove duplicate days
), r AS (
  SELECT user_id, day,
         ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY day) AS rn
  FROM d
)
SELECT user_id,
       MIN(day) AS start_day, MAX(day) AS end_day, COUNT(*) AS days
FROM r
GROUP BY user_id, date(day, '-' || rn || ' day')     -- the island key
ORDER BY user_id, start_day;
```

- `date(day, '-3 day')` is sqlite's way to subtract 3 days from a date text.
- Inside an island, `day` and `rn` both increase by 1, so the key date is the same.
- In PostgreSQL you would write `day - rn * INTERVAL '1 day'`.

| day | rn | key = day − rn |
|---|---|---|
| 01-01 | 1 | 12-31 |
| 01-02 | 2 | 12-31 |
| 01-05 | 3 | 01-02 |

```check
{"q": "Why do we need SELECT DISTINCT user_id, day before ROW_NUMBER?", "type": "single", "options": ["Two logins on one day would increase rn without increasing the day, which breaks the constant key", "To make the query faster", "To sort the days"], "answer": 0, "why": ["Correct.", "Speed is not the reason.", "ORDER BY sorts."]}
```

## Fill missing dates with a recursive CTE
A table with sales has **no row** for days without sales. A chart or a moving average needs a row for every day. Make a **calendar** with a [[recursive CTE]], then `LEFT JOIN`:

```sql
WITH RECURSIVE cal(day) AS (
  SELECT MIN(day) FROM daily                          -- start
  UNION ALL
  SELECT date(day, '+1 day') FROM cal                 -- next day
  WHERE day < (SELECT MAX(day) FROM daily)            -- stop
)
SELECT cal.day, COALESCE(d.revenue, 0) AS revenue
FROM cal LEFT JOIN daily d ON d.day = cal.day
ORDER BY cal.day;
```

- The first `SELECT` is the **anchor** (the first day).
- The second `SELECT` is the **recursive step** (add one day). The `WHERE` makes it stop.
- `LEFT JOIN` keeps every calendar day. `COALESCE(x, 0)` replaces [[NULL]] by 0.
- Is zero the right fill? For sales yes. For a temperature, no: keep NULL or use the last value.

```check
{"q": "What does the WHERE day < max_day do inside the recursive part?", "type": "single", "options": ["Stops the recursion at the last date", "Filters the sales", "Sorts the calendar"], "answer": 0, "why": ["Correct: without it the recursion would not end.", "It filters the calendar, not the sales.", "ORDER BY sorts."]}
```

## First event per user
Use `ROW_NUMBER()` and keep rows with number 1:

```sql
SELECT user_id, event_id, event_type, event_time
FROM (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY event_time, event_id) AS rn
  FROM events
)
WHERE rn = 1
ORDER BY user_id;
```

- `PARTITION BY user_id` makes one list per user.
- The second sort key `event_id` is a **[[tie-breaker]]**, so the result is always the same.
- For the **last** event use `ORDER BY event_time DESC`.
- `MIN(event_time)` with `GROUP BY` gives only the time, not the other columns of that row.

```chart
{"title": "Daily sales with missing days (zeros added)", "x": "day", "height": 200, "series": [{"name": "revenue (missing days filled with 0)", "y": [12, 15, 0, 0, 18, 20, 0, 14, 16, 0, 13, 17], "kind": "bar"}], "caption": "Without the calendar, the zero days would not exist as rows. A moving average over rows would then be wrong."}
```

```check
{"q": "You need the whole row of each user's first event. Which is best?", "type": "single", "options": ["ROW_NUMBER() with rn = 1", "GROUP BY user_id with MIN(event_time) only", "ORDER BY event_time LIMIT 1"], "answer": 0, "why": ["Correct.", "That gives the time but not the other columns of the row.", "LIMIT 1 returns one row for the whole table, not per user."]}
```

## Worked example
Islands and a filled calendar on small tables.

```python
import sqlite3
import pandas as pd

con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE logins (user_id TEXT, day TEXT)")
con.executemany("INSERT INTO logins VALUES (?, ?)", [
    ("a", "2024-01-01"), ("a", "2024-01-02"), ("a", "2024-01-02"), ("a", "2024-01-03"),
    ("a", "2024-01-05"), ("b", "2024-01-10")])

islands = """
WITH d AS (SELECT DISTINCT user_id, day FROM logins),
r AS (SELECT user_id, day, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY day) AS rn FROM d)
SELECT user_id, MIN(day) AS start_day, MAX(day) AS end_day, COUNT(*) AS days
FROM r GROUP BY user_id, date(day, '-' || rn || ' day')
ORDER BY user_id, start_day
"""
print(pd.read_sql_query(islands, con).to_string(index=False))

con.execute("CREATE TABLE daily (day TEXT, revenue REAL)")
con.executemany("INSERT INTO daily VALUES (?, ?)", [("2024-01-01", 10), ("2024-01-02", 20), ("2024-01-05", 50)])
fill = """
WITH RECURSIVE cal(day) AS (
  SELECT MIN(day) FROM daily
  UNION ALL
  SELECT date(day, '+1 day') FROM cal WHERE day < (SELECT MAX(day) FROM daily))
SELECT cal.day, COALESCE(d.revenue, 0) AS revenue
FROM cal LEFT JOIN daily d ON d.day = cal.day ORDER BY cal.day
"""
print(pd.read_sql_query(fill, con).to_string(index=False))

# Output:
# user_id  start_day    end_day  days
#       a 2024-01-01 2024-01-03     3
#       a 2024-01-05 2024-01-05     1
#       b 2024-01-10 2024-01-10     1
#        day  revenue
# 2024-01-01     10.0
# 2024-01-02     20.0
# 2024-01-03      0.0
# 2024-01-04      0.0
# 2024-01-05     50.0
```

## Common mistakes
- Forgetting `DISTINCT` in the islands query.
- Computing `ROW_NUMBER` without `PARTITION BY user_id` (islands then mix users).
- A recursive [[CTE]] without a stop condition (an endless loop).
- Filling with 0 when 0 has a different meaning from "no data".
- `LIMIT 1` or `MIN()` when you need the whole first row per user.
- Comparing text dates in a format that does not sort (use `YYYY-MM-DD`).

## Interview lens
**Typical question:** "Given a table of logins, return each user's longest [[streak]] of consecutive days."

**Strong answer:** This is gaps and islands. I take distinct user and day. I number the rows per user by day with `ROW_NUMBER()`. Then I subtract the row number, in days, from the date. The result is constant inside a streak, so I group by user and that key and count the days. The longest streak is the maximum count per user. The cost is one sort, O(n log n). For missing dates I would build a calendar with a recursive CTE and left join. For "first event per user" I use `ROW_NUMBER() ... = 1` with a tie-breaker.

**Red flags:** a self-join with many conditions; no `DISTINCT`; an unbounded recursion; no tie-breaker in `ROW_NUMBER`.

## Real world
- Recursive common table expressions are part of the SQL standard (SQL:1999). SQLite 3.8.3 and later, PostgreSQL, MySQL 8 and others support them.
- Dashboards usually fill missing days before they draw a line. A missing day and a zero day look different on a chart.

## Key points
- Islands in SQL: `DISTINCT`, then `ROW_NUMBER() OVER (PARTITION BY ... ORDER BY day)`, group by `day − rn`.
- Fill missing dates with a `WITH RECURSIVE` calendar and a `LEFT JOIN`. Use `COALESCE` only when 0 is the right fill.
- First event per user: `ROW_NUMBER() ... WHERE rn = 1`, with a tie-breaker.
- Always give recursion a stop condition.
