---
slug: monthly-clip-lag
title: Monthly Aggregation, Clipping and a Lag Feature
difficulty: Medium
type: function
tags: [kaggle, predict-future-sales, groupby, clip, lag]
skills: [pandas-fluency, leakage]
packages: []
companies_style: [Kaggle Predict Future Sales]
---
In *Predict Future Sales* (1C Company) the data has one row per **sale line**: `date_block_num` (month number 0, 1, 2, ...), `shop_id`, `item_id`, `item_cnt_day` (units sold that day; returns are negative). The task is to predict the **monthly** count for each shop and item. The scoring clips the true target to the range **[0, 20]**, so you train on a clipped target too.

Write `monthly_clip_lag(df, lo=0, hi=20)`:

1. Sum `item_cnt_day` for each (`date_block_num`, `shop_id`, `item_id`). Call it `item_cnt_month`.
2. Clip `item_cnt_month` to the range `[lo, hi]`.
3. Add `lag_1`: the clipped `item_cnt_month` of the **same shop and item in the previous month** (`date_block_num − 1`). If there is no row for that month, use `0.0`.

Return a DataFrame with columns `date_block_num, shop_id, item_id, item_cnt_month, lag_1`, sorted by those first three columns, with index `0, 1, 2, ...`. Only the (month, shop, item) groups that have at least one sale line appear.

### Example 1
**Input:**
```
date_block_num shop_id item_id item_cnt_day
0              1       10      3
0              1       10      4
1              1       10      30
1              2       10      -1
```
**Output:**
```
date_block_num shop_id item_id item_cnt_month lag_1
0              1       10      7.0             0.0
1              1       10      20.0            7.0
1              2       10      0.0             0.0
```
**Explanation:** Month 0 sums to 7. Month 1 sums to 30 and is clipped to 20; its lag is 7. Shop 2 has a net return of −1, clipped to 0.

### Constraints
- 0 ≤ rows ≤ 10^5
- `lo` ≤ `hi`

### Hints
1. `groupby([...], as_index=False)["item_cnt_day"].sum()`, then `clip(lo, hi)`.
2. Make a copy of the result with `date_block_num + 1` and the column renamed to `lag_1`.
3. Merge it back on (`date_block_num`, `shop_id`, `item_id`) with `how="left"` and fill NaN with 0.0.

### Solution explanation
Clip **after** summing, as the competition does for the monthly target. The lag trick: shift the month number of a copy of the table forward by one and merge. That is a leakage-safe lag because it only uses the previous month. Time O(n log n). Common bugs: clipping each daily row instead of the monthly sum, merging on month without shop and item, and using `shift` on a table that has missing months (it shifts by rows, not months).
