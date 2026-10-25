---
slug: dtw-distance-window
title: DTW Distance with a Window
difficulty: Medium
type: function
tags: [dtw, dynamic-programming, classification]
skills: [ts-classification, from-scratch]
packages: []
companies_style: [activity recognition]
---
Compute the **Dynamic Time Warping** distance between two lists of numbers `a` and `b`.

- The cost of matching `a[i]` with `b[j]` is `abs(a[i] - b[j])`.
- `D[i][j]` is the smallest total cost to match the first `i` values of `a` with the first `j` values of `b`. `D[0][0] = 0`. All other border cells are infinity.
- `D[i][j] = cost + min(D[i-1][j], D[i][j-1], D[i-1][j-1])`.
- The answer is `D[n][m]`.

`window` limits the match: only cells with `abs(i - j) <= w` may be used, where `w = max(window, abs(n - m))`. If `window` is `None`, there is no limit.

Return the distance as a float. If `a` or `b` is empty, return `inf` (use `float("inf")`).

### Example 1
**Input:** `a = [0, 1, 2, 1, 0]`, `b = [0, 0, 1, 2, 1, 0]`, `window = None`
**Output:** `0.0`
**Explanation:** The first 0 of `a` matches both zeros of `b`; all other pairs are equal.

### Example 2
**Input:** `a = [1, 5, 1]`, `b = [1, 1, 5]`, `window = 0`
**Output:** `8.0`
**Explanation:** With window 0 the path is the diagonal: |1-1| + |5-1| + |1-5| = 8.

### Constraints
- 0 <= len(a), len(b) <= 2000
- window is None or an integer >= 0

### Hints
1. Make a table of size (n+1) by (m+1) filled with infinity and set `D[0][0] = 0`.
2. For row `i` only loop over `j` from `max(1, i - w)` to `min(m, i + w)`.
3. If you want O(m) memory, keep only the previous row.

### Solution explanation
**Approach.** Dynamic programming over a table. Each cell takes the best of three neighbours (up, left, diagonal) plus the local cost. The window skips cells far from the diagonal.

**Why it works.** Every warping path ends by entering the last cell from one of those three cells, so the best total cost is built from the best costs of smaller problems.

**Complexity.** Without a window: O(n · m) time. With window w: O(n · w) time (about n · (2w + 1) cells). Space: O(n · m) for the full table, or O(m) if you keep two rows.

**Common bugs.** Forgetting `w >= |n − m|`; indexing `a[i]` instead of `a[i-1]`; filling the border with 0 instead of infinity; returning the square root when the task asks for the sum of absolute differences.
