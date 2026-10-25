---
slug: make-sliding-windows
title: Build Sliding Windows for a Neural Network
difficulty: Medium
type: function
tags: [numpy, windowing, deep-learning]
skills: [from-scratch, leakage]
packages: []
companies_style: [demand forecasting, sensor data]
---
A neural network needs examples of the same size. You make them by sliding a window over a series.
Each example has an **input** (the past) and a **target** (the future values that come right after it).

Write `make_windows(series, input_len, horizon, stride=1)`.

- `series` is a numpy array with shape `[time]` or `[time, features]`. If it has one dimension, treat it as one feature.
- Column 0 is the value you want to predict.
- Return `(X, y)`.
  - `X` has shape `[n, input_len, features]`: the past values of all features.
  - `y` has shape `[n, horizon]`: the next `horizon` values of column 0.
- The first window starts at row 0. The next one starts `stride` rows later. Keep only windows that fit fully inside the series.
- If no window fits, return empty arrays: `X` with shape `[0, input_len, features]` and `y` with shape `[0, horizon]`.

### Example 1
**Input:** `make_windows(np.arange(6.0), 3, 2)`
**Output:** `X` = `[[[0],[1],[2]], [[1],[2],[3]]]`, `y` = `[[3,4],[4,5]]`
**Explanation:** Total window length is 3 + 2 = 5. A series of 6 points has 6 − 5 + 1 = 2 windows.

### Example 2
**Input:** `make_windows(np.arange(8.0), 2, 1, stride=3)`
**Output:** `X` shape `(2, 2, 1)`, `y` = `[[2],[5]]`
**Explanation:** Windows start at rows 0 and 3. Row 6 would need rows 6, 7, 8, and row 8 does not exist.

### Constraints
- `1 <= input_len`, `1 <= horizon`, `1 <= stride`
- `0 <= len(series) <= 10^5`
- Do not use a Python loop over windows (use `sliding_window_view` or index arrays).

### Hints
1. The number of windows is `(T - input_len - horizon) // stride + 1` when `T >= input_len + horizon`.
2. `np.lib.stride_tricks.sliding_window_view(s, total, axis=0)` gives every window of length `total`. The window axis comes last.
3. Move the window axis back with `.transpose(0, 2, 1)`, take every `stride`-th window with `[::stride]`, then split the first `input_len` rows (X) from the rest (y, column 0 only). Use `.copy()` so the result owns its memory.

### Solution explanation
1. Turn a 1D series into `[T, 1]`.
2. Build all windows of length `input_len + horizon` with `sliding_window_view` (no data is copied yet, it is a view).
3. Keep every `stride`-th window, reorder axes to `[n, time, features]`.
4. Split: the first `input_len` rows are X, the next `horizon` rows of column 0 are y.

Time `O(n * (input_len + horizon) * features)` for the final copy. The view itself is `O(1)`.
Common bugs: forgetting the empty case, returning y with all features, and a window that goes past the end of the series.
