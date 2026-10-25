---
slug: idempotent-forecast-upsert
title: Idempotent Forecast Backfill
difficulty: Easy
type: function
tags: [pandas, pipeline, backfill, idempotency]
skills: [ml-system-design, pandas-fluency]
packages: []
companies_style: [retail demand, batch scoring]
---
A forecast table has one row per `(date, series_id)`. A backfill job produces new forecasts for some past dates. Merge them so that the job is **idempotent**: running it twice gives the same table as running it once.

Write `upsert_forecasts(existing, new)`.

- Both tables have columns `date`, `series_id`, `yhat`, `version`.
- A row in `new` **replaces** the row in `existing` with the same `(date, series_id)`.
- Rows of `existing` without a match stay. Rows of `new` without a match are added.
- If `new` itself has several rows for the same key, the **last** one wins.
- Return the table sorted by `date`, then `series_id`, with index `0..n-1`. Do not change the inputs.

### Example 1
**Input:**
```
existing: (d1, A, 10, v1), (d1, B, 20, v1)
new:      (d1, B, 25, v2), (d2, A, 30, v2)
```
**Output:** `(d1, A, 10, v1), (d1, B, 25, v2), (d2, A, 30, v2)`
**Explanation:** `(d1, B)` is replaced. `(d2, A)` is new. `(d1, A)` is untouched.

### Constraints
- Up to 200 000 rows. `date` is a datetime column, `series_id` a string.
- `existing` or `new` can be empty.

### Hints
1. Put both tables together with `pd.concat`. Put `existing` first.
2. `drop_duplicates(subset=[...], keep="last")` keeps the newest row per key.
3. Sort with `sort_values(["date", "series_id"])` and reset the index. Check: `upsert(upsert(a, b), b)` must equal `upsert(a, b)`.

### Solution explanation
Concatenate existing and new (in that order), keep the last row of each `(date, series_id)`, sort, reset the index. Because new rows come last, they win, and a repeated run changes nothing: the same keys are replaced by the same rows. Complexity: O((n + m) log(n + m)). Common bugs: `keep="first"` (old rows win), forgetting the sort, and appending without removing duplicates.
