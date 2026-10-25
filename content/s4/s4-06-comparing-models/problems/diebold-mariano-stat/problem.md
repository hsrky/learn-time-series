---
slug: diebold-mariano-stat
title: Diebold-Mariano Statistic
difficulty: Hard
type: function
tags: [dm-test, comparison, statistics]
skills: [metrics, from-scratch]
packages: []
---
Implement a simple Diebold-Mariano test for two forecasts on the same test points.

`dm_test(e1, e2, h=1, power=2)`

- `e1`, `e2`: forecast errors (actual − forecast) of model 1 and model 2, equal length `n`.
- Loss: `L(e) = |e| ** power` (`power=2` is squared error, `power=1` is absolute error).
- `d = L(e1) − L(e2)`, `dbar = mean(d)`.
- Long-run variance of `d` (the variance of the mean must allow for autocorrelation at horizon `h`):
  `V = g0 + 2 * sum_{k=1}^{h-1} g_k`, where `g_k = (1/n) * sum_{t=k}^{n-1} (d[t] − dbar) * (d[t−k] − dbar)` (divide by `n`, not `n − k`).
- `stat = dbar / sqrt(V / n)`.
- Two-sided p-value from the standard normal: `p = erfc(|stat| / sqrt(2))` (use `math.erfc`).
- Return a dictionary `{"stat": stat, "p_value": p}`.
- If `V <= 0` or `n < 2`, return `{"stat": nan, "p_value": nan}`.

A negative `stat` means model 1 has the smaller loss.

### Example 1
**Input:** `e1=[1, -1, 1, -1]`, `e2=[2, -2, 2, -2]`, `h=1`, `power=2`

**Output:** `{"stat": nan, "p_value": nan}`

**Explanation:** `d = [-3, -3, -3, -3]`. All values equal, so `V = 0`. The result is `nan`.

### Example 2
**Input:** `e1=[1, 2, 1, 2]`, `e2=[2, 2, 2, 3]`, `h=1`, `power=1`

**Output:** `stat ≈ -3.464`, `p_value ≈ 0.0005`

**Explanation:** `d = [-1, 0, -1, -1]`, `dbar = -0.75`, `g0 = 0.1875`, `stat = -0.75 / sqrt(0.1875 / 4) = -3.464`.

### Constraints
- 0 ≤ n ≤ 10^5, `1 ≤ h ≤ n`, `power` in {1, 2}.

### Hints
1. Build `d` and subtract the mean before you compute autocovariances.
2. `g_k = np.sum(dc[k:] * dc[:n-k]) / n`, where `dc = d - dbar`.
3. If `V` is not positive (for example because of strong negative autocorrelation), return `nan`.

### Solution explanation
The statistic is the mean loss difference divided by its standard error. For `h = 1` the standard error is `sqrt(g0 / n)`. For longer horizons, forecast errors overlap, so autocovariances up to lag `h − 1` are added. The p-value uses the normal approximation. Time O(n·h). Common bugs: dividing autocovariances by `n − k`, which can make `V` negative, and forgetting the factor 2.
