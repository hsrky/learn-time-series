---
slug: time-based-split
title: Time-Based Train/Test Split
difficulty: Easy
type: function
tags: [pandas, split, leakage]
skills: [leakage, pandas-fluency]
packages: []
companies_style: [demand forecasting, retail]
---
You get a table `df` with a `DatetimeIndex`. The rows may be **out of order**.

Write `time_split(df, cutoff, gap_days=0)` that returns two tables `(train, test)`:

- `test` has all rows with a date **on or after** `cutoff`.
- `train` has all rows with a date **before** `cutoff - gap_days` days. The gap removes the days just before the cutoff, so that features built from recent days cannot reach into the test set.
- Both tables must be sorted by date, oldest first.
- Do not change the values. Do not shuffle.
- If a part is empty, return an empty table with the same columns.

`cutoff` is a string such as `"2024-01-10"` or a `pd.Timestamp`.

### Example 1
**Input:** daily rows from `2024-01-01` to `2024-01-10` (values 0 to 9), `cutoff="2024-01-08"`, `gap_days=0`

**Output:** `train` has the dates 01-01 to 01-07, `test` has 01-08 to 01-10.

**Explanation:** The cutoff day itself belongs to the test set.

### Example 2
**Input:** the same rows, `cutoff="2024-01-08"`, `gap_days=2`

**Output:** `train` has 01-01 to 01-05, `test` has 01-08 to 01-10.

**Explanation:** `cutoff - 2 days` is 01-06. Train keeps only dates before 01-06. Days 01-06 and 01-07 are dropped.

### Constraints
- 0 ≤ number of rows ≤ 10^5.
- `gap_days` is an integer ≥ 0.
- The index has no duplicates.

### Hints
1. First sort the table by its index.
2. Turn `cutoff` into a `pd.Timestamp` and compute the train limit with `pd.Timedelta(days=gap_days)`.
3. Use boolean masks on the index: `df.index < limit` and `df.index >= cutoff`.

### Solution explanation
1. Sort by index with `sort_index()`.
2. `limit = cutoff - gap_days` days.
3. `train = df[df.index < limit]`, `test = df[df.index >= cutoff]`.

Boolean masks keep the columns even when no row matches, so the empty case works without extra code.
Time: O(n log n) for the sort, space O(n). Common bug: using `<=` for train or `>` for test, which moves the cutoff row to the wrong side. Another bug: `train_test_split` with `shuffle=True`.
