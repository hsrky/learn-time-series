---
slug: ses-fit-alpha
title: Fit Alpha by Grid Search
difficulty: Medium
type: function
tags: [ses, grid-search, one-step-error]
skills: [from-scratch, backtest]
packages: []
companies_style: [demand forecasting]
---
Choose the smoothing parameter alpha of simple exponential smoothing by minimising the one-step squared error.

Write `fit_ses_alpha(y, grid)`. For each `alpha` in `grid`:

1. Start with `level = y[0]`.
2. For each `t = 1, ..., n-1`: the forecast of `y[t]` is `level`. The error is `e = y[t] - level`. Then update `level = level + alpha * e`.
3. `sse(alpha)` is the sum of the squared errors `e`.

Return a dict `{"alpha": best_alpha, "sse": sse_of_best, "forecast": final_level}`, where `best_alpha` has the smallest SSE (on a tie, the **smaller** alpha) and `forecast` is the level after the last value for that alpha. Round `sse` and `forecast` to 4 decimals.

### Example 1
**Input:** `fit_ses_alpha([10, 14, 12, 16], [0.25, 0.5, 0.75, 1.0])`
**Output:** `{"alpha": 0.75, "sse": 31.0625, "forecast": 15.0625}`
**Explanation:** The SSE values are 39.5625 (alpha 0.25), 32.0 (0.5), 31.0625 (0.75) and 36.0 (1.0). The smallest is at alpha = 0.75.

### Example 2
**Input:** `fit_ses_alpha([5, 5, 5, 5], [0.1, 0.9])`
**Output:** `{"alpha": 0.1, "sse": 0.0, "forecast": 5.0}`
**Explanation:** All errors are 0, so the tie goes to the smaller alpha.

### Constraints
- `2 <= len(y) <= 10^4`, `1 <= len(grid) <= 200`, all `0 <= alpha <= 1`.
- Do not use the data after position `t` when you forecast `y[t]`.

### Hints
1. Write a helper `sse_and_level(y, alpha)` that returns the pair.
2. Loop over the grid. Compare with `<` (strict), and sort the grid first so ties go to the smaller alpha.
3. Round only at the end.

### Solution explanation
For each alpha we run SES once, so the time is O(len(grid) * n). The error uses only past data, so there is no leakage. Alpha is tuned on training data only. Common bugs: counting the first point's error (there is no forecast for it), picking the larger alpha on ties, and using absolute errors instead of squared errors.
