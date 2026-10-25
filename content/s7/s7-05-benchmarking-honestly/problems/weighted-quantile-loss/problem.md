---
slug: weighted-quantile-loss
title: Weighted Quantile Loss (WQL)
difficulty: Medium
type: function
tags: [probabilistic, pinball-loss, benchmark]
skills: [metrics, uncertainty]
packages: []
---
Foundation models often output **quantiles** (for example the 10%, 50% and 90% values) instead of one number.
Benchmarks score them with the **weighted quantile loss** (WQL), based on the pinball loss.

For one quantile level `q`, forecast `f` and true value `y`, let `e = y − f`. The **pinball loss** is `max(q·e, (q − 1)·e)`.

`WQL = mean over q of [ 2 · sum_t pinball(q, y_t, f_q,t) / sum_t |y_t| ]`

Write `wql(y, quantile_forecasts, levels)`:

- `y` has shape `[time]`.
- `quantile_forecasts` has shape `[n_levels, time]`, one row per level.
- `levels` is a list like `[0.1, 0.5, 0.9]`.
- Return one float. If `sum(|y|) == 0`, return `nan`.

### Example 1
**Input:** `y=[10, 20]`, `levels=[0.5]`, forecasts `[[12, 18]]`
**Output:** `0.1333...`
**Explanation:** Errors are −2 and +2. Pinball at q=0.5: 0.5·2 = 1 each, sum 2. WQL = 2·2 / 30 = 0.1333.

### Constraints
- `1 <= time <= 10^5`, `1 <= n_levels <= 99`.

### Hints
1. `e = y[None, :] - quantile_forecasts` has shape `[n_levels, time]`.
2. Use `np.maximum(q * e, (q - 1) * e)` with `q = np.array(levels)[:, None]`.
3. Sum over time (axis 1), divide by `sum(|y|)`, multiply by 2, average over levels.

### Solution explanation
A low quantile such as 0.1 punishes a forecast *above* the truth with weight 0.9, and a forecast *below* it with weight 0.1.
So each quantile row is pushed to the right level. The factor 2 makes WQL at q=0.5 equal to the sum of absolute errors divided by the sum of the target.
Time `O(levels·time)`. Common bug: using `q` and `1−q` the wrong way round.
