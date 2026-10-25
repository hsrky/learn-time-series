---
slug: revin-normalize
title: Reversible Instance Normalization (RevIN)
difficulty: Medium
type: function
tags: [revin, normalization, distribution-shift]
skills: [from-scratch, leakage]
packages: []
---
Series change level over time (**distribution shift**). **RevIN** fixes this for a neural network:

1. **Normalize** each input window with its *own* mean and standard deviation (per sample, per channel).
2. Run the model on the normalized window.
3. **Denormalize** the model output with the *same* mean and standard deviation.

Write two functions. Shapes: `x` is `[batch, time, channels]`.

`revin_normalize(x, gamma, beta, eps=1e-5)`

- `mean` = mean over the time axis, shape `[batch, 1, channels]`.
- `std` = `sqrt(var + eps)`, where `var` is the population variance (divide by n) over time, shape `[batch, 1, channels]`.
- `xn = (x − mean) / std * gamma + beta`. `gamma` and `beta` have shape `[channels]` (learned scale and shift).
- Return `(xn, mean, std)`.

`revin_denormalize(y, mean, std, gamma, beta)`

- `y` has shape `[batch, horizon, channels]`.
- Return `(y − beta) / gamma * std + mean`.

### Example 1
**Input:** `x = [[[1],[2],[3]]]`, `gamma=[1]`, `beta=[0]`
**Output:** `xn ≈ [[[-1.2247],[0],[1.2247]]]`, `mean = 2`, `std ≈ 0.8165`
**Explanation:** Variance = (1 + 0 + 1)/3 = 0.667, std = 0.8165.

### Example 2
**Input:** denormalize the normalized values again.
**Output:** `[[[1],[2],[3]]]` — the round trip gives back the input.

### Constraints
- `gamma` has no zero entries. `1 <= time <= 1000`, `batch >= 0`.

### Hints
1. `x.mean(axis=1, keepdims=True)` keeps the shape `[batch, 1, channels]`.
2. `x.var(axis=1, keepdims=True)` uses the population variance by default (ddof=0).
3. Broadcasting does the rest: `gamma` of shape `[channels]` is applied on the last axis.

### Solution explanation
The model only sees "shape" (values around 0 with spread 1). The level and scale come back at the end, so the forecast is on the original scale.
Time `O(batch·time·channels)`. Common bugs: using the sample variance, normalizing over the batch axis, and forgetting to undo `gamma` and `beta` before the mean and std.
