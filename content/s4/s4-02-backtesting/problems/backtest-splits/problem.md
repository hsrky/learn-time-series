---
slug: backtest-splits
title: Backtest Splitter Generator
difficulty: Medium
type: function
tags: [backtest, generator, walk-forward]
skills: [backtest, from-scratch]
packages: []
---
Write a **generator** `backtest_splits(n, initial, horizon, step=None, window=None, gap=0)` that yields one fold at a time as a tuple `(train_idx, test_idx)`. Both are `numpy` integer arrays of positions `0 … n-1`.

Rules:
- The first fold ends its training part at position `initial` (exclusive). So the first training positions end at `initial - 1`.
- Each next fold moves the end of training by `step` positions. If `step` is `None`, use `horizon`.
- `window=None` means an **expanding** window: train starts at 0. If `window` is an integer, use a **sliding** window: train is the last `window` positions before the end (but not before 0).
- `gap` positions are skipped between the end of training and the start of the test part.
- `test_idx` has exactly `horizon` positions, starting at `end + gap`.
- Yield only **complete** folds: the test part must fit inside `n` positions.

### Example 1
**Input:** `list(backtest_splits(10, 6, 2))`

**Output:** two folds: train `[0..5]` test `[6, 7]`; train `[0..7]` test `[8, 9]`.

**Explanation:** `step` defaults to the horizon 2. A third fold would need positions 10 and 11.

### Example 2
**Input:** `list(backtest_splits(12, 4, 2, step=2, window=3, gap=1))`

**Output:** train `[1,2,3]` test `[5,6]`; train `[3,4,5]` test `[7,8]`; train `[5,6,7]` test `[9,10]`.

**Explanation:** The window keeps 3 points. The gap of 1 skips one point (4, 6, 8) before each test part.

### Constraints
- 1 ≤ `initial`, `horizon`, `n` ≤ 10^5. `step ≥ 1`. `gap ≥ 0`. `window ≥ 1` or `None`.
- If no fold fits, the generator yields nothing.

### Hints
1. Keep a variable `end` that starts at `initial`. Loop while the test part fits.
2. The test part is `np.arange(end + gap, end + gap + horizon)`.
3. For the train part use `start = 0` or `max(0, end - window)`. Then add `step` to `end`.

### Solution explanation
A `while` loop over the training end `end`. The loop condition `end + gap + horizon <= n` guarantees a complete test window. Inside, compute `start` from `window`, yield `np.arange(start, end)` and `np.arange(end+gap, end+gap+horizon)`, and move `end += step`. Time O(number of folds × fold size). Common bug: `<` instead of `<=` in the loop condition, which drops the last valid fold.
