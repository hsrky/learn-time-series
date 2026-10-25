---
slug: rolling-conformal
title: Rolling-Window Conformal Intervals
difficulty: Hard
type: function
tags: [conformal, rolling, backtest, intervals]
skills: [uncertainty, backtest, from-scratch]
packages: []
---
You have actual values `y` and one-step-ahead forecasts `yhat` (same length `n`). For each time `t`, build an interval for `yhat[t]` from the **last `window` absolute residuals that are already known at time `t`**. That means the residuals `|y[s] − yhat[s]|` for `s = t−window … t−1`. Never use `y[t]` or later values.

Write `rolling_conformal(y, yhat, alpha, window)` that returns two arrays `(lower, upper)` of length `n`.

For each `t`:
- Let `r` be the available residuals (at most `window`, fewer at the start). Let `m = len(r)`.
- If `m == 0`: `lower[t] = upper[t] = nan`.
- Otherwise `k = ceil(round((m + 1) * (1 - alpha), 9))`. If `k <= m`, `q` is the `k`-th smallest value of `r`; else `q = inf`.
- `lower[t] = yhat[t] − q`, `upper[t] = yhat[t] + q`.

Residuals that are `nan` (for example because `yhat` is `nan` at the start) must be **skipped** when they are collected: take the last `window` time steps, then drop the `nan` values.

### Example 1
**Input:** `y=[10, 12, 11, 14, 13]`, `yhat=[9, 13, 11, 12, 13]`, `alpha=0.5`, `window=3`

**Output:** `q = [nan, 1, 1, 1, 1]`, so `lower = yhat − q` and `upper = yhat + q`

**Explanation:** Residuals are `[1, 1, 0, 2, 0]`. At `t=0` there is none, so `nan`. At `t=1` one residual `[1]`: `k = ceil(2 × 0.5) = 1`, so `q = 1`. At `t=2`: residuals `[1, 1]`, `k = ceil(3 × 0.5) = 2`, `q = 1`. At `t=3`: residuals `[1, 1, 0]` sorted `[0, 1, 1]`, `k = ceil(4 × 0.5) = 2`, `q = 1`. At `t=4`: window is steps 1..3 → `[1, 0, 2]` sorted `[0, 1, 2]`, `k = 2`, `q = 1`.

### Constraints
- 1 ≤ `n` ≤ 5000, `window ≥ 1`, `0 < alpha < 1`.

### Hints
1. Compute all residuals once: `res = np.abs(y - yhat)`.
2. For each `t`, slice `res[max(0, t - window):t]` and drop the `nan` values.
3. Reuse the rank formula from split conformal; remember `q = inf` when `k > m`.

### Solution explanation
A loop over `t` with a slice of known residuals. Sorting each slice costs O(window log window), so the total is O(n · window log window). The slice ends at `t` (exclusive), which keeps the method free of look-ahead. A faster version keeps a sorted list and inserts/removes one value per step. Common bugs: slicing `res[t-window:t+1]` (leak) and a negative start index (`t - window < 0`) that wraps around.
