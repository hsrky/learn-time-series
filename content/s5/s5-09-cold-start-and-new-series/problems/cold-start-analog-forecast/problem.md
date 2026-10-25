---
slug: cold-start-analog-forecast
title: Cold-Start Forecast from Similar Series
difficulty: Medium
type: function
tags: [cold-start, analogs, numpy, new-series]
skills: [scale, baseline-first, from-scratch]
packages: []
---
A new product has only `L` days of history. Older, similar products ("analogs") have full histories, already **aligned by age** (position 0 is the launch day of each product).

Write `cold_start_forecast(new_hist, analogs, horizon, k=2)`:

1. `new_hist` is a list of `L` numbers (`L` may be 0). `analogs` is a list of lists. `horizon ≥ 1`.
2. **Valid analogs**: length at least `L + horizon`, and a positive mean over their first `L` days (when `L > 0`).
3. If `L == 0`: return the average, over **all analogs with length ≥ `horizon`**, of their values at ages `0 … horizon−1` (raw values, no scaling). If there is no such analog, return an array of `nan`.
4. If `L > 0` and the mean of `new_hist` is `0`, return zeros.
5. If `L > 0` and there is no valid analog, return the mean of `new_hist` repeated `horizon` times.
6. Otherwise, for each valid analog compute the shape distance
   `d = mean(|new_hist / mean(new_hist) − analog[:L] / mean(analog[:L])|)`.
   Pick the `k` analogs with the smallest `d` (ties: the lower position in the list wins; use all valid ones if there are fewer than `k`).
7. The forecast is the average over the chosen analogs of `analog[L:L+horizon] / mean(analog[:L])`, multiplied by `mean(new_hist)`.

Return a `numpy` array of length `horizon`.

### Example 1
**Input:** `new_hist=[5, 7, 9]`, `analogs=[[10, 14, 18, 21, 21], [100, 100, 100, 100, 100]]`, `horizon=2`, `k=1`

**Output:** `[10.5, 10.5]`

**Explanation:** Shape of the new product: `[5, 7, 9] / 7 = [0.71, 1, 1.29]`. Analog 0: `[10, 14, 18] / 14` is the same shape (`d = 0`). Analog 1 is flat (`d > 0`). The best analog continues with `21 / 14 = 1.5` twice. Forecast: `7 × 1.5 = 10.5`.

### Constraints
- 0 ≤ L ≤ 1000, up to 1000 analogs, 1 ≤ `horizon` ≤ 100, `k ≥ 1`.

### Hints
1. Filter the valid analogs first, and keep their original positions for tie-breaking.
2. `np.argsort(d, kind="stable")[:k]` keeps the lower position first when distances tie.
3. Divide the analog's future by the mean of its **first L** days, not by its overall mean.

### Solution explanation
This is a nearest-neighbour forecast on normalized shapes. Normalizing by the first-`L` mean puts all products on the same scale. The final multiplication moves the shape to the level of the new product. Time O(A·(L + horizon)) for A analogs. Common bugs: scaling by the wrong mean, forgetting the length check, and unstable tie-breaking.
