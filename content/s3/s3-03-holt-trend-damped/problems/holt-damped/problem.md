---
slug: holt-damped
title: Holt's Method with Damped Trend
difficulty: Medium
type: function
tags: [holt, damped-trend, exponential-smoothing]
skills: [from-scratch]
packages: []
companies_style: [revenue forecasting]
---
Implement Holt's linear trend method, with an optional damping parameter `phi`.

Write `holt(y, alpha, beta, h, phi=1.0)`. Use these exact rules.

Start values: `level = y[0]`, `trend = y[1] - y[0]`.

For every `t = 1, ..., n-1` (use all values from the second one on):

- `new_level = alpha * y[t] + (1 - alpha) * (level + phi * trend)`
- `trend = beta * (new_level - level) + (1 - beta) * phi * trend`
- `level = new_level`

Return a dict:

- `"level"`: the final level
- `"trend"`: the final trend
- `"forecast"`: a list of length `h`. For step `j = 1..h` it is `level + (phi + phi^2 + ... + phi^j) * trend`.

With `phi = 1` this is Holt's linear method.

### Example 1
**Input:** `holt([10, 12, 15], 0.5, 0.5, 2)`
**Output:** `{"level": 14.5, "trend": 2.25, "forecast": [16.75, 19.0]}`
**Explanation:** Step by step: after 12 the state is (12, 2). After 15 the state is (14.5, 2.25).

### Example 2
**Input:** `holt([10, 12, 15], 0.5, 0.5, 2, phi=0.8)`
**Output:** `{"level": 14.08, "trend": 1.82, "forecast": [15.536, 16.7008]}`
**Explanation:** The forecast is `level + 0.8 * trend` and `level + 1.44 * trend`.

### Constraints
- `2 <= len(y) <= 10^5`, `0 <= alpha, beta <= 1`, `0 < phi <= 1`, `0 <= h <= 1000`
- Return floats (plain Python lists).

### Hints
1. Initialise `level` and `trend` from the first two values.
2. Inside the loop, compute the new level first. The trend update uses both the new and the old level.
3. For the forecast use `np.cumsum(phi ** np.arange(1, h + 1))`.

### Solution explanation
It is one pass over the data with two states, so time is O(n + h). The damped sum `phi + phi^2 + ... + phi^j` is a cumulative sum of powers. Common bugs: updating the trend with the new level before saving the old one, forgetting `phi` in the level update, and using `h * trend` for a damped forecast.
