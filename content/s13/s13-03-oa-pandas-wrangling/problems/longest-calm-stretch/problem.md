---
slug: longest-calm-stretch
title: Longest Calm Stretch
difficulty: Easy
type: function
tags: [window, two-pointers, arrays]
skills: [from-scratch]
packages: []
companies_style: [monitoring, OA warm-up]
---
A list `values` holds one number per day. A **calm stretch** is a run of consecutive days where the change from each day to the next is at most `tol` in absolute value.

Return the length (in days) of the longest calm stretch. A single day is a calm stretch of length 1. For an empty list return `0`.

### Example 1
**Input:** `values = [10, 11, 11, 20, 21, 22, 40]`, `tol = 1`
**Output:** `3`
**Explanation:** Days 1 to 3 (`10, 11, 11`) are calm: changes 1 and 0. Days 4 to 6 (`20, 21, 22`) are also calm, with length 3. The jump from 11 to 20 breaks the first run.

### Example 2
**Input:** `values = [5, 5, 5]`, `tol = 0`
**Output:** `3`

### Constraints
- 0 ≤ len(values) ≤ 10^6
- `tol` ≥ 0
- Values are integers or floats

### Hints
1. Walk through the list once. Keep the length of the current calm run.
2. If `abs(values[i] - values[i-1]) <= tol`, the run grows by 1. Otherwise it restarts at 1.
3. Keep the best length seen so far. Handle the empty list first.

### Solution explanation
One pass with a counter. For each day compare with the previous day. If the change is within `tol`, extend the run. Otherwise start a new run of length 1. Track the maximum. Time O(n), space O(1). A common bug is to compare with the first day of the run instead of the previous day, or to start the counter at 0 for a single-day list.
