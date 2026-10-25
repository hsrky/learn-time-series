---
slug: dlinear-forward
title: DLinear Forward Pass
difficulty: Medium
type: function
tags: [dlinear, decomposition, linear-models]
skills: [from-scratch, baseline-first]
packages: []
---
**DLinear** (Zeng et al., 2023) is a very simple forecaster. It has two steps:

1. **Decompose** each input window into a *trend* and a *remainder*.
   The trend is a moving average with an odd `kernel` size. At both ends, repeat the first and last value
   `(kernel − 1) // 2` times, so the average has the same length as the input. The remainder is `x − trend`.
2. Apply **one linear layer to each part** and add the results:
   `out = trend @ W_trend + remainder @ W_rem`

Write `dlinear_forward(x, W_trend, W_rem, kernel)`:

- `x` has shape `[batch, L]` (L past steps).
- `W_trend` and `W_rem` have shape `[L, H]` (H future steps).
- Return an array with shape `[batch, H]`.

### Example 1
**Input:** `x = [[1,2,3,4,5]]`, `kernel=3`, and both weight matrices equal to the identity-like "copy the last step" (`W[-1,:]=1`, others 0), H = 2.
**Output:** `[[5., 5.]]`
**Explanation:** Trend of the last point = mean(4, 5, 5) = 4.667. Remainder = 5 − 4.667 = 0.333. Sum = 5.

### Constraints
- `kernel` is odd, `1 <= kernel <= L`
- `1 <= L <= 1000`, `1 <= H <= 500`, `batch >= 0`

### Hints
1. Pad: `np.concatenate([first_values, x, last_values], axis=1)` where `first_values = np.repeat(x[:, :1], (kernel-1)//2, axis=1)`.
2. Moving average with a cumulative sum, or `sliding_window_view(padded, kernel, axis=1).mean(-1)`.
3. Final answer: `trend @ W_trend + (x - trend) @ W_rem`.

### Solution explanation
The trend part learns "how to extend the slow movement", the remainder part learns "how to extend the repeating pattern".
There are only `2·L·H` weights. On long-term forecasting benchmarks this tiny model beat many Transformers (see the lesson).
Time `O(batch·L·H)`. Common bugs: zero padding (it pulls the trend toward 0 at the ends), and an even kernel.
