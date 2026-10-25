---
slug: nbeats-residual-stack
title: N-BEATS Residual Stacking
difficulty: Medium
type: function
tags: [nbeats, residual, numpy]
skills: [from-scratch]
packages: []
---
In N-BEATS, blocks are chained. Each block reads the **residual** of the earlier blocks and returns a
**backcast** and a **forecast**. For this task, each block is a plain linear map (no hidden layers):

- `backcast = r @ Wb`, with `Wb` of shape `[L, L]`
- `forecast = r @ Wf`, with `Wf` of shape `[L, H]`

Write `nbeats_forward(x, blocks)`:

- `x` has shape `[batch, L]`.
- `blocks` is a list of pairs `(Wb, Wf)`.
- Start with `r = x`. For each block: compute the backcast and the forecast from `r`, then set `r = r − backcast`, and add the forecast to a running sum.
- Return `(forecast_sum, r)`: the summed forecast with shape `[batch, H]` and the final residual with shape `[batch, L]`.
- If `blocks` is empty, the horizon is unknown, so return `(None, x)`.

### Example 1
**Input:** `x = [[1, 2]]`, one block with `Wb = identity(2)`, `Wf = [[1],[1]]`
**Output:** forecast `[[3.]]`, residual `[[0., 0.]]`
**Explanation:** The backcast equals the input, so nothing is left. The forecast is 1 + 2 = 3.

### Constraints
- `0 <= batch <= 1000`, `1 <= L <= 200`, `1 <= H <= 100`, up to 30 blocks.

### Hints
1. Keep two variables: `r` (residual) and `total` (forecast sum).
2. `@` is the matrix product. Shapes: `[batch, L] @ [L, L]` and `[batch, L] @ [L, H]`.
3. Start `total` as `None`, and add the first forecast, or start with zeros after you read `H` from the first block.

### Solution explanation
Each block removes the part of the input it can explain. The forecasts of all blocks add up. This is the same "peel the onion" idea as boosting on residuals.
Time `O(blocks · batch · L · (L + H))`.
Common bugs: adding the backcast instead of subtracting, and using the original `x` for every block.
