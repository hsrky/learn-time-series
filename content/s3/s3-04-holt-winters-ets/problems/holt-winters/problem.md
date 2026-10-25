---
slug: holt-winters
title: Holt-Winters (Additive and Multiplicative)
difficulty: Hard
type: function
tags: [holt-winters, ets, seasonality, exponential-smoothing]
skills: [from-scratch, baseline-first]
packages: []
companies_style: [retail demand, energy load]
---
Implement Holt-Winters exponential smoothing with a level, a trend and a seasonal part. Use these exact rules, so that your result matches the reference.

Write `holt_winters(y, m, alpha, beta, gamma, h, seasonal="add")`. `m` is the season length. Raise `ValueError` if `len(y) < 2 * m`.

**Start values (from the first two seasons):**

1. `centre = mean(y[0:m])`
2. `trend = (mean(y[m:2m]) - centre) / m`
3. `line[i] = centre + trend * (i - (m - 1) / 2)` for `i = 0..m-1` (a straight line through season 1)
4. `season[i] = y[i] - line[i]` (additive) or `y[i] / line[i]` (multiplicative)
5. `level = line[m-1]`

**Update for every `t = m, ..., n-1`** with `i = t % m`, `s_old = season[i]`, `expected = level + trend`:

- Additive:
  - `new_level = alpha * (y[t] - s_old) + (1 - alpha) * expected`
  - `season[i] = gamma * (y[t] - expected) + (1 - gamma) * s_old`
- Multiplicative:
  - `new_level = alpha * (y[t] / s_old) + (1 - alpha) * expected`
  - `season[i] = gamma * (y[t] / expected) + (1 - gamma) * s_old`
- Both: `trend = beta * (new_level - level) + (1 - beta) * trend`, then `level = new_level`.

**Forecast** for `j = 1..h`: `base = level + j * trend`, `s = season[(n - 1 + j) % m]`. The forecast is `base + s` (additive) or `base * s` (multiplicative).

Return a dict `{"level", "trend", "season": [m floats], "forecast": [h floats]}`.

### Example 1
**Input:** `holt_winters([10, 20, 30, 40, 12, 22, 32, 42], 4, 0.5, 0.5, 0.5, 4)`
**Output:** `{"level": 27.75, "trend": 0.5, "season": [-14.25, -4.75, 4.75, 14.25], "forecast": [14.0, 24.0, 34.0, 44.0]}`
**Explanation:** The data repeats a pattern with a small growth of 0.5 per step. The model learns it exactly.

### Example 2
**Input:** a clean series `(20 + 0.5 t) * (1 + 0.25 sin(2 pi t / 12))` for `t = 0..47`, `seasonal="mul"`, `m = 12`.
**Output:** the forecast for the next 12 steps is close to the true continuation (within about 0.2).

### Constraints
- `2 * m <= len(y) <= 10^5`, `m >= 2`, `0 <= alpha, beta, gamma <= 1`, `0 <= h <= 1000`
- For `seasonal="mul"` assume all values of `y` are positive.

### Hints
1. Store the seasonal values in an array of length `m`. The position of time `t` is `t % m`.
2. Compute `expected = level + trend` before you change anything. Use it for the new level and for the season update.
3. Update the trend with the new level and the old level. Then replace the level.

### Solution explanation
The start values fit a line through the first season. This removes the bias that a trend would put into the seasonal values. Then one pass over the data updates level, trend and one seasonal value per step. Time O(n + h), space O(m). The multiplicative version divides instead of subtracting, which fits series where the season grows with the level. Common bugs: using the new level in the season update (it must be the old expected value), indexing the season with `t - m` instead of `t % m`, and using `h` for the seasonal index of the forecast.
