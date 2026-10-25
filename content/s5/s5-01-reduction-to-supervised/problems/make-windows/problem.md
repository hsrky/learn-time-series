---
slug: make-windows
title: Sliding Windows to X and y
difficulty: Easy
type: function
tags: [numpy, windows, supervised]
skills: [from-scratch, leakage]
packages: []
---
Write `make_windows(y, window, horizon=1, stride=1)`. It turns a 1-D series into a supervised table.

- `X` has one row per window. Each row is `window` consecutive values.
- `Y` has the next `horizon` values after the window (so `Y` has `horizon` columns).
- The first window starts at position 0. Each next window starts `stride` positions later.
- Only **complete** rows are allowed: both the window and its `horizon` targets must lie inside `y`.
- Return `(X, Y)` as `numpy` float arrays with shapes `(rows, window)` and `(rows, horizon)`. If there is no complete row, return arrays with 0 rows.

### Example 1
**Input:** `y=[3, 5, 4, 6, 8, 7]`, `window=3`, `horizon=1`

**Output:** `X=[[3,5,4],[5,4,6],[4,6,8]]`, `Y=[[6],[8],[7]]`

**Explanation:** `6 − 3 − 1 + 1 = 3` rows.

### Example 2
**Input:** `y=[1, 2, 3, 4, 5, 6, 7]`, `window=2`, `horizon=2`, `stride=2`

**Output:** `X=[[1,2],[3,4]]`, `Y=[[3,4],[5,6]]`

**Explanation:** Starts at 0, 2, 4. The start 4 needs positions 4 to 7, but the last index is 6, so it is dropped.

### Constraints
- 0 ≤ len(`y`) ≤ 10^5. `window`, `horizon`, `stride` ≥ 1.

### Hints
1. The last start position `s` must satisfy `s + window + horizon <= len(y)`.
2. Make the list of starts with `np.arange(0, len(y) - window - horizon + 1, stride)`.
3. Use index arithmetic: `starts[:, None] + np.arange(window)` gives all feature positions at once.

### Solution explanation
Compute all start positions, then use fancy indexing to build `X` and `Y` without a Python loop. The number of rows (with stride 1) is `n − window − horizon + 1`. Time and memory O(rows × (window + horizon)). Common bug: an off-by-one in the last start, which drops the final valid row or reads past the end.
