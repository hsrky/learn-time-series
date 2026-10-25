---
slug: longest-login-streak
title: Longest Login Streak
difficulty: Easy
type: function
tags: [islands, dates, python]
skills: [streaming-algorithms]
packages: []
companies_style: []
---
You get a list `days` of date strings in `YYYY-MM-DD` form, in any order, possibly with duplicates. Return a tuple `(length, start, end)` for the **longest run of consecutive calendar days**. `start` and `end` are date strings.

If two runs have the same length, return the one that starts first. For an empty list return `(0, None, None)`.

### Example 1
**Input:** `days = ['2024-03-01', '2024-03-02', '2024-03-02', '2024-03-03', '2024-03-05']`
**Output:** `(3, '2024-03-01', '2024-03-03')`
**Explanation:** After removing the duplicate: 1, 2, 3 March is a run of 3 days. 5 March is a run of 1.

### Constraints
- 0 <= len(days) <= 10^5
- Dates are valid; the run can cross a month or year (including leap days)

### Hints
1. `datetime.date.fromisoformat(s).toordinal()` turns a date into a day number.
2. `sorted(set(...))` removes duplicates and sorts.
3. Walk once; the next day continues the run when it is previous + 1. Use `date.fromordinal` for the output.

### Solution explanation
**Approach.** Convert to day numbers, remove duplicates, sort, then scan once keeping the current run start and length. Update the best only when the run is strictly longer (so the earlier run wins ties).

**Why it works.** Consecutive calendar days differ by exactly 1 in ordinal numbers, even across months and leap years.

**Complexity.** O(n log n) time for the sort, O(n) space for the set. The scan is O(n).

**Common bugs.** Counting duplicates; comparing strings instead of dates; replacing the best on equal length (breaks the tie rule).
