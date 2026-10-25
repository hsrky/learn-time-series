---
slug: daily-oil-fill
title: Daily Oil Price with Gaps Filled
difficulty: Easy
type: function
tags: [kaggle, store-sales, reindex, ffill, missing-data]
skills: [pandas-fluency]
packages: []
companies_style: [Kaggle Store Sales]
---
In the Store Sales competition the file `oil.csv` has columns `date` and `dcoilwtico` (the oil price). It has **no rows for weekends and holidays**, and some prices are missing (`NaN`). The sales data has a row for **every** day. To use oil as a feature you need one price for every calendar day.

Write `daily_oil(oil, start, end)`:

- `oil` is a DataFrame with columns `date` (datetime) and `dcoilwtico` (float, may contain NaN). Rows can be in any order. Each date appears at most once.
- Return a DataFrame with columns `date` and `dcoilwtico` with **one row for each calendar day** from `start` to `end` (both included, strings or timestamps).
- Fill each missing price with the **last known price before it** (forward fill). The forward fill may use a price from before `start`.
- If there is no earlier price (the first days), use the **next known price** (backward fill).
- If there is no price at all, return NaN for every day.
- Index: `0, 1, 2, ...`.

### Example 1
**Input:** oil prices `Fri 2024-01-05: 70.0`, `Mon 2024-01-08: 72.0`; `start = 2024-01-05`, `end = 2024-01-09`
**Output:**
```
date        dcoilwtico
2024-01-05  70.0
2024-01-06  70.0
2024-01-07  70.0
2024-01-08  72.0
2024-01-09  72.0
```
**Explanation:** Saturday and Sunday use Friday's price. Tuesday (after the last known price) uses Monday's price.

### Constraints
- 0 ≤ rows in `oil` ≤ 10^5
- `start` ≤ `end`, at most 10^5 days

### Hints
1. Set `date` as the index and sort it.
2. Make a full daily index that covers both your range and the oil dates, and `reindex` to it.
3. Use `ffill()` and then `bfill()`. Finally select the rows from `start` to `end`.

### Solution explanation
Forward fill carries the last known price into the weekend. We must reindex over a range that also covers dates **before** `start`, otherwise the first days of the range have no earlier price to copy. Backward fill covers the case where the range starts before the first known price. Time O(n + days). Common bugs: using only the range `start..end` (loses earlier prices), filling backward first (copies future prices into the past), and dropping NaN rows before the reindex (which loses the information that a price is missing).
