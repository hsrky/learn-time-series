---
id: s9-08-sql-window-functions
title: SQL window functions for time series
minutes: 35
level: intermediate
goals: [Write LAG and LEAD queries, Compute a moving average with a frame, Compute running totals per group]
prereqs: []
tags: [sql, window-functions, sqlite]
skills: [sql-time-series]
---
## Warm-up
```check
{"q": "Which SQL clause makes groups of rows and returns ONE row per group?", "type": "single", "options": ["GROUP BY", "ORDER BY", "LIMIT"], "answer": 0, "why": ["Correct.", "ORDER BY only sorts.", "LIMIT cuts the number of rows."]}
```
```check
{"q": "`SELECT day, revenue FROM daily ORDER BY day` returns the rows in which order?", "type": "single", "options": ["Increasing day", "Random order", "Largest revenue first"], "answer": 0, "why": ["Correct. Text dates like 2024-01-05 sort correctly.", "ORDER BY gives a defined order.", "That needs ORDER BY revenue DESC."]}
```

## Why it matters
Most real time-series data lives in a **database**. An OA often asks: "Write a SQL query that shows the day-over-day change." "Compute a 7-day moving average." "Show the [[running total]] per store." You can do each of these in **one query** with **[[window]] functions**. They keep every row (unlike `GROUP BY`) and add a new column that looks at the neighbouring rows.

The practice problems use **sqlite**, a small database that runs in your browser. It supports window functions. Dates are stored as text in the form `YYYY-MM-DD`; this sorts in the right order.

## LAG and LEAD: look at the previous or next row
`LAG(col)` gives the value of the row before; `LEAD(col)` the row after. The `OVER (ORDER BY day)` part defines the order.

```sql
SELECT day, revenue,
       LAG(revenue)  OVER (ORDER BY day) AS prev_revenue,
       revenue - LAG(revenue) OVER (ORDER BY day) AS change
FROM daily
ORDER BY day;
```

| day | revenue | prev_revenue | change |
|---|---|---|---|
| 2024-01-01 | 100 | [[NULL]] | NULL |
| 2024-01-02 | 130 | 100 | 30 |
| 2024-01-03 | 120 | 130 | −10 |

- The first row has no previous row, so the result is `NULL` (missing). `LAG(col, 1, 0)` can give a default instead.
- `LEAD` works the same, looking forward.
- Add `PARTITION BY store` inside `OVER (...)` to restart for every store.

**Warning:** LAG looks at the previous **row**, not the previous **day**. If a day is missing, the result is wrong (the "change" spans two days). Fill missing days first (next lesson).

```check
{"q": "What does LAG(revenue) return for the first row of the ordered set?", "type": "single", "options": ["NULL", "0", "The same row's revenue"], "answer": 0, "why": ["Correct: there is no earlier row.", "Only if you give a default with LAG(revenue, 1, 0).", "That is the value of the current row."]}
```

## Moving average with a frame
A **[[frame]]** tells the [[window function]] which rows around the current row to use:

```sql
AVG(revenue) OVER (ORDER BY day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)
```

This is the average of the current row and the **6 rows before it**: a 7-row (7-day) moving average.

- `ROWS BETWEEN 6 PRECEDING AND CURRENT ROW` counts **rows**.
- The first 6 rows have fewer than 7 rows in the frame. The average is then over fewer rows. To return `NULL` instead, use `CASE WHEN COUNT(*) OVER (same frame) = 7 THEN ... END`.
- It is the SQL version of `s.rolling(7).mean()`.

```chart
{"title": "Daily revenue and its 7-day moving average", "x": "day", "height": 220, "series": [{"name": "revenue", "gen": [["const", {"value": 100}], ["season", {"period": 7, "amp": 20}], ["noise", {"sd": 6}]], "n": 56, "seed": 14}, {"name": "7-day average (flat: the weekly pattern is removed)", "gen": [["const", {"value": 100}]], "n": 56, "dash": true}], "caption": "Averaging over exactly one full week removes the weekly pattern."}
```

```check
{"q": "Which frame gives a 3-row moving average that includes the current row?", "type": "single", "options": ["ROWS BETWEEN 2 PRECEDING AND CURRENT ROW", "ROWS BETWEEN 3 PRECEDING AND CURRENT ROW", "ROWS BETWEEN CURRENT ROW AND 2 FOLLOWING"], "answer": 0, "why": ["Correct: 2 before + the current row = 3 rows.", "That is 4 rows.", "That looks forward (future rows)."]}
```

## Running totals per group
A **running total** ([[cumulative sum]]) adds up all rows from the start to the current row. Use `SUM(...) OVER (PARTITION BY ... ORDER BY ...)`:

```sql
SELECT store, day, amount,
       SUM(amount) OVER (PARTITION BY store ORDER BY day
                         ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total
FROM orders
ORDER BY store, day;
```

- `PARTITION BY store` restarts the total for each store.
- `ORDER BY day` sets the order inside a store.
- Write the frame explicitly. If you leave it out and use `ORDER BY`, SQL uses `RANGE`, and **rows with the same `day` get the same total** (they are "peers").

```check
{"q": "Two orders of one store have the same day. You use SUM() OVER (PARTITION BY store ORDER BY day) without a frame. What happens?", "type": "single", "options": ["Both rows show the same running total (peers)", "An error", "The second row is removed"], "answer": 0, "why": ["Correct: the default frame is RANGE, which includes all rows with the same day.", "No error is raised.", "Rows are never removed by a window function."]}
```

## Worked example
Run the three ideas in one query on a small table.

```python
import sqlite3
import pandas as pd

con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE daily (day TEXT, store TEXT, revenue REAL)")
rows = [("2024-01-01", "A", 100), ("2024-01-02", "A", 130), ("2024-01-03", "A", 120), ("2024-01-04", "A", 150),
        ("2024-01-01", "B", 10), ("2024-01-02", "B", 20)]
con.executemany("INSERT INTO daily VALUES (?, ?, ?)", rows)

query = """
SELECT store, day, revenue,
       revenue - LAG(revenue) OVER (PARTITION BY store ORDER BY day)            AS change,
       AVG(revenue) OVER (PARTITION BY store ORDER BY day
                          ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)             AS avg_3,
       SUM(revenue) OVER (PARTITION BY store ORDER BY day
                          ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)    AS running
FROM daily
ORDER BY store, day
"""
print(pd.read_sql_query(query, con).round(2).to_string(index=False))

# Output:
# store        day  revenue  change  avg_3  running
#     A 2024-01-01    100.0     NaN 100.00    100.0
#     A 2024-01-02    130.0    30.0 115.00    230.0
#     A 2024-01-03    120.0   -10.0 116.67    350.0
#     A 2024-01-04    150.0    30.0 133.33    500.0
#     B 2024-01-01     10.0     NaN  10.00     10.0
#     B 2024-01-02     20.0    10.0  15.00     30.0
```

## Common mistakes
- Forgetting `ORDER BY` inside `OVER (...)` (the order is then undefined).
- Forgetting the final `ORDER BY` of the query: the output order is not guaranteed.
- Using `LAG` when days are missing.
- Using `RANGE` (the default) when you want `ROWS`.
- Mixing up `PRECEDING 7` (8 rows) and `PRECEDING 6` (7 rows).

## Interview lens
**Typical question:** "Write a query that returns each day's revenue, the change from the previous day, and the 7-day moving average."

**Strong answer:** I use window functions over the daily table ordered by day. `revenue - LAG(revenue) OVER (ORDER BY day)` gives the change. `AVG(revenue) OVER (ORDER BY day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)` gives the 7-row average; I use a `CASE` with `COUNT(*) OVER` the same frame to return NULL for the first 6 days. I mention that these look at rows, not calendar days, so I would first make sure each day exists exactly once. For several stores I add `PARTITION BY store`. The cost is one sort, O(n log n).

**Red flags:** self-joins for LAG; correlated sub-queries in a loop; not mentioning missing days; `GROUP BY` where a window function is needed.

## Real world
- Window functions are part of the SQL standard (SQL:2003) and are supported by PostgreSQL, MySQL 8, SQL Server, BigQuery, Snowflake and SQLite 3.25 and later.
- Moving averages of daily counts are the standard way to show trends in dashboards (for example 7-day averages in public health reports).

## Key points
- Window functions keep all rows and add a column computed from related rows.
- `LAG`/`LEAD` read the previous/next row; the first/last row gives NULL.
- A frame such as `ROWS BETWEEN 6 PRECEDING AND CURRENT ROW` gives a 7-row moving average.
- `SUM() OVER (PARTITION BY g ORDER BY t ROWS ...)` gives a running total per group.
- Windows work on rows, not calendar days: fix missing days first.
