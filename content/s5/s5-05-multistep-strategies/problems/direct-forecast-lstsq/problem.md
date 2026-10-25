---
slug: direct-forecast-lstsq
title: Direct Multi-Step Forecast with Least Squares
difficulty: Medium
type: function
tags: [numpy, lstsq, direct, multi-step]
skills: [from-scratch]
packages: []
---
Write `direct_forecast(y, p, h)`. Use the **direct** strategy: train one linear model per horizon step.

For each step `k = 1 … h`:
1. Build a table from all windows of `y`. Features: `p` consecutive values `y[i], …, y[i+p-1]` plus a constant `1`. Target: the value `k` steps after the window, `y[i+p+k-1]`.
2. Fit the weights with `np.linalg.lstsq(A, target, rcond=None)`.
3. The forecast for step `k` is the model applied to the **last** `p` values of `y` (plus the constant 1).

Return a `numpy` array of length `h`. If there are not enough points to build at least one row for step `k` (that is `len(y) − p − k + 1 < 1`), the forecast for that step is `nan`.

### Example 1
**Input:** `y = [1, 2, 3, 4, 5, 6]`, `p = 2`, `h = 3`

**Output:** `[7, 8, 9]`

**Explanation:** On a straight line every step model fits exactly. Step 3 has `6 − 2 − 3 + 1 = 2` training rows.

### Example 2
**Input:** `y = [1, 2, 3, 4]`, `p = 1`, `h = 2`

**Output:** `[5, 6]`

**Explanation:** Step 1 has 3 rows (`1→2`, `2→3`, `3→4`) and fits exactly. Step 2 has 2 rows (`1→3`, `2→4`) and also fits exactly: the model is `y(t+2) = y(t) + 2`, so the forecast is `4 + 2 = 6`. If `h = 5`, step 4 has `4 − 1 − 4 + 1 = 0` rows, so the forecast for step 4 is `nan`.

### Constraints
- 2 ≤ len(`y`) ≤ 10^4, 1 ≤ `p` < len(`y`), 1 ≤ `h` ≤ 100.

### Hints
1. Write a helper `windows(y, p, k)` that returns the feature matrix and the target vector.
2. The number of rows is `len(y) - p - k + 1`; stop with `nan` when it is below 1.
3. All models use the same input: the last `p` values of the series, with the constant 1 appended.

### Solution explanation
Each step has its own fit, so there is no feedback of errors. The price is `h` least-squares problems. Later steps have fewer training rows. Time O(h·n·p²). A common bug is using the recursive loop by mistake, or shifting the target by `k` instead of `k − 1` positions after the window.
