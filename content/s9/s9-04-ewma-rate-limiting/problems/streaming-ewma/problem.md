---
slug: streaming-ewma
title: Streaming EWMA
difficulty: Easy
type: class
tags: [streaming, ewma, class]
skills: [streaming-algorithms]
packages: []
companies_style: []
---
Write a class `StreamingEWMA(alpha)`.

- `update(x)`: add the value `x` and return the new smoothed value.
- The first value is returned as it is. After that: `s = alpha * x + (1 - alpha) * s`.
- `update_at(x, t, tau)`: a version for irregular times. Let `dt = t - last_t` (the time since the previous call to `update_at`). Use `a = 1 - exp(-dt / tau)` and `s = a * x + (1 - a) * s`. The first call returns `x` and stores `t`.

Use only O(1) memory. The two methods are tested separately (never mixed on one object).

### Example 1
**Input:** `alpha = 0.5`, values `10, 20, 30`
**Output:** `[10, 15.0, 22.5]`
**Explanation:** 10, then 0.5·20 + 0.5·10 = 15, then 0.5·30 + 0.5·15 = 22.5.

### Constraints
- 0 < alpha <= 1
- tau > 0 and timestamps do not decrease

### Hints
1. Store the current value `s` (None at the start).
2. The first call must return `x` itself.
3. For `update_at` also store the last timestamp; `math.exp` is in the `math` module (already imported in the tests).

### Solution explanation
**Approach.** One number of state (two for the timestamp version). Each call mixes the new value into the old estimate.

**Why it works.** Unrolling the formula shows that a value from j steps ago has weight `alpha (1 − alpha)^j`: the weights decrease exponentially and sum to 1.

**Complexity.** O(1) time and O(1) memory per update.

**Common bugs.** Starting from 0; swapping `alpha` and `1 - alpha`; using `dt` in the wrong sign.
