---
slug: pinball-loss
title: Pinball (Quantile) Loss
difficulty: Easy
type: function
tags: [quantile, loss, probabilistic]
skills: [uncertainty, from-scratch, metrics]
packages: []
---
Write `pinball_loss(y_true, y_pred, tau)`. It returns the **mean pinball loss** of a quantile forecast.

For one point with actual `y` and forecast `q`:
- if `y >= q`: loss = `tau * (y - q)`
- if `y < q`: loss = `(1 - tau) * (q - y)`

The result is the mean over all points. If the inputs are empty, return `nan`. `tau` is a number with `0 < tau < 1`.

Also write `weighted_quantile_loss(y_true, preds, taus)`. `preds` is a list with one forecast array per level in `taus`. Return `2 * sum_over_levels(sum_over_points(pinball loss)) / (len(taus) * sum(|y_true|))`, that is the pinball losses summed over points, averaged over the levels, doubled and divided by the total actual. If `sum(|y_true|) == 0`, return `nan`.

### Example 1
**Input:** `y_true=[100]`, `y_pred=[90]`, `tau=0.9`

**Output:** `9.0`

**Explanation:** The forecast is 10 too low. Loss = 0.9 × 10.

### Example 2
**Input:** `y_true=[100]`, `y_pred=[110]`, `tau=0.9`

**Output:** `1.0`

**Explanation:** The forecast is 10 too high. Loss = (1 − 0.9) × 10.

### Constraints
- 0 ≤ length ≤ 10^5. `0 < tau < 1`. Values are finite floats.

### Hints
1. Compute `d = y - q` with numpy.
2. `np.where(d >= 0, tau * d, (tau - 1) * d)` gives both cases at once.
3. For the weighted version, loop over the levels and add up the sums.

### Solution explanation
The two branches can be written as `max(tau*d, (tau-1)*d)`, a convex function with a kink at 0 (that is the "pinball" shape). Averaging gives the loss. The weighted version is the pinball loss summed over many levels and scaled by the total actual; it is a standard way to compare probabilistic models over many series. Time O(n × levels). A common bug is to swap `tau` and `1 − tau`.
