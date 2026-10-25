---
slug: croston-forecast
title: Croston and SBA Forecast
difficulty: Medium
type: function
tags: [croston, sba, intermittent-demand, from-scratch]
skills: [from-scratch, metrics]
packages: []
companies_style: [spare parts, slow-moving retail]
---
Implement Croston's method for intermittent demand, with the SBA correction.

Write `croston(y, alpha, variant="croston")`. `y` is a list of non-negative demands per period (many zeros).

1. If `y` has no positive value, return `0.0`.
2. Let `first` be the index of the first positive value. Start with `z = y[first]` (size), `p = first + 1` (interval), and `last = first`.
3. For every later index `t` with `y[t] > 0`:
   - `q = t - last`
   - `z = alpha * y[t] + (1 - alpha) * z`
   - `p = alpha * q + (1 - alpha) * p`
   - `last = t`

   For periods with `y[t] == 0` change nothing.
4. The forecast per period is `z / p`. If `variant == "sba"`, multiply by `(1 - alpha / 2)`.

Return a float. Raise `ValueError` for any other value of `variant`.

### Example 1
**Input:** `croston([0, 0, 5, 0, 0, 0, 3, 0, 4], 0.5)`
**Output:** `1.4545...`
**Explanation:** First demand at t = 2 (0-based): z = 5, p = 3. Then t = 6: z = 4, p = 3.5. Then t = 8: z = 4, p = 2.75. 4 / 2.75 = 1.4545.

### Example 2
**Input:** `croston([0, 0, 5, 0, 0, 0, 3, 0, 4], 0.5, variant="sba")`
**Output:** `1.0909...` (that is 0.75 * 1.4545)

### Constraints
- `1 <= len(y) <= 10^5`, `0 < alpha <= 1`, all `y[t] >= 0`.

### Hints
1. Find the first demand with `np.nonzero(y > 0)[0]`.
2. Loop over the later indices. Use an `if y[t] > 0:` branch and do nothing otherwise.
3. Remember that `p` starts at `first + 1`, the number of periods up to and including the first demand.

### Solution explanation
Croston smooths two series separately: the size of the demands and the interval between them. Updating only at demands means long gaps do not drag the size estimate down. Their ratio is the average demand per period. SBA corrects the positive bias of the ratio. Time O(n). Common bugs: updating `z` in zero periods, starting `p` at 0 or 1, and forgetting to update `last`.
