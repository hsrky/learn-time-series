---
slug: combine-reports
title: Combine Two Daily Reports
difficulty: Easy
type: function
tags: [pandas, index-alignment, series]
skills: [pandas-fluency]
packages: []
companies_style: [logistics]
---
Two warehouses send daily shipment counts as pandas Series. Their dates (the index) are not the same. A day with no report means **0 shipments**.

Write `combine_reports(a, b)`. Return one Series with the total shipments per day. It must contain every date from **either** Series, sorted by date. Dates that are missing in one Series count as 0.

### Example 1
**Input:**
`a = pd.Series([8, 9], index=pd.to_datetime(["2024-03-01", "2024-03-02"]))`
`b = pd.Series([5, 6], index=pd.to_datetime(["2024-03-02", "2024-03-03"]))`
**Output:** a Series with 2024-03-01 → 8, 2024-03-02 → 14, 2024-03-03 → 6
**Explanation:** Only 2024-03-02 is in both. The other two days use 0 for the missing partner.

### Constraints
- Each Series has between 0 and 10^5 values.
- The indexes are `DatetimeIndex` objects without duplicates. They may be unsorted.
- Values may be integers or floats. A NaN value means "no report" and counts as 0.

### Hints
1. Plain `a + b` gives NaN for days that are in only one Series.
2. Look at the `fill_value` argument of `Series.add`.
3. Use `sort_index()` at the end. Use `fillna(0)` first if the values contain NaN.

### Solution explanation
1. `a.fillna(0).add(b.fillna(0), fill_value=0)` aligns on the union of both indexes. A missing partner counts as 0.
2. `sort_index()` puts the dates in order.

Time O((n + m) log(n + m)) because of sorting. Common bug: `a + b` gives NaN where only one Series has a report.
