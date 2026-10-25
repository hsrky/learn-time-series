---
slug: longest-stable-window
title: Longest Stable Period
difficulty: Hard
type: function
tags: [sliding-window, deque, two-pointers]
skills: [streaming-algorithms, from-scratch]
packages: []
companies_style: []
---
A sensor gives you `readings`. A period is **stable** if the largest reading minus the smallest reading in it is at most `limit`. Return the **length of the longest stable period** (a block of consecutive readings). Return 0 for an empty list.

Your solution must run in O(n) time.

### Example 1
**Input:** `readings = [8, 2, 4, 7]`, `limit = 4`
**Output:** `2`
**Explanation:** The period [2, 4] has range 2 and length 2. The period [4, 7] also has length 2. No period of length 3 has a range of 4 or less.

### Example 2
**Input:** `readings = [10, 1, 2, 4, 7, 2]`, `limit = 5`
**Output:** `4`
**Explanation:** The period [1, 2, 4, 7, 2] has range 6, too big. [2, 4, 7, 2] has range 5, length 4.

### Constraints
- 0 <= len(readings) <= 10^5
- limit >= 0

### Hints
1. Use two pointers: `left` and `right`. Grow `right` one step at a time.
2. Keep a decreasing deque for the maximum and an increasing deque for the minimum.
3. While `max - min > limit`, move `left` forward and pop deque fronts that are before `left`.

### Solution explanation
**Approach.** Sliding window with two monotonic deques: one gives the maximum, one the minimum of the current window. For each new `right`, add it to both deques. While the range is too big, increase `left` and remove deque fronts whose index is below `left`. The best length is `right - left + 1`.

**Why it works.** If a window is stable, all its sub-windows are stable, so `left` only moves forward. That makes the two-pointer scan valid.

**Complexity.** O(n) time (every index enters and leaves each deque once; `left` and `right` only move forward). O(n) worst-case extra space for the deques.

**Common bugs.** Shrinking only one step instead of using `while`; forgetting to pop deque fronts after moving `left`; storing values instead of indices.
