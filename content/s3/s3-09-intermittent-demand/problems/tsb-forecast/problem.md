---
slug: tsb-forecast
title: TSB Forecast for Obsolescence
difficulty: Medium
type: function
tags: [tsb, intermittent-demand, obsolescence]
skills: [from-scratch, metrics]
packages: []
companies_style: [spare parts, slow-moving retail]
---
Croston's method never changes during a long run of zeros. The TSB method (Teunter, Syntetos, Babai) fixes this by smoothing the **probability** of demand in **every** period.

Write `tsb(y, alpha, beta)`.

1. If `y` has no positive value, return `0.0`.
2. Let `first` be the index of the first positive value. Start with `z = y[first]` and `prob = 1 / (first + 1)`.
3. For every later index `t`:
   - if `y[t] > 0`: `z = alpha * y[t] + (1 - alpha) * z` and `prob = beta + (1 - beta) * prob`
   - else: `prob = (1 - beta) * prob`
4. Return `prob * z`.

Also write `tsb_path(y, alpha, beta)` that returns a list with the forecast after each period (the value `prob * z` after processing period `t`; `0.0` before the first demand). Its last value equals `tsb(y, alpha, beta)`.

### Example 1
**Input:** `tsb([0, 0, 5, 0, 0, 0, 3, 0, 4], 0.5, 0.2)`
**Output:** `1.6615...`
**Explanation:** Follow the update rules. The probability rises at each demand and falls in the zeros.

### Example 2
**Input:** `tsb([3, 3, 3, 0, 0, 0, 0], 0.5, 0.5)`
**Output:** `0.1875`
**Explanation:** After the three 3s the probability is 1 (start 1, and each demand keeps it at 1). Four zeros halve it four times: 1 / 16 = 0.0625. Then `0.0625 * 3 = 0.1875`.

### Constraints
- `1 <= len(y) <= 10^5`, `0 < alpha <= 1`, `0 < beta <= 1`, `y[t] >= 0`.

### Hints
1. The probability update is `prob = beta * (y[t] > 0) + (1 - beta) * prob` in all periods after the first demand.
2. `z` changes only when `y[t] > 0`.
3. For `tsb_path`, append `prob * z` after each period (use `0.0` before the first demand).

### Solution explanation
TSB tracks two things: the chance that a period has demand, and the size of a demand. The forecast is their product. Because the chance is updated in every period, a long run of zeros makes it shrink exponentially, so the forecast falls. Time O(n). Common bugs: updating `z` in zero periods, not updating `prob` in zero periods (that gives Croston-like behaviour), and a wrong start for `prob`.
