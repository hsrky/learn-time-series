---
slug: causal-conv1d
title: Causal Convolution and Receptive Field
difficulty: Medium
type: function
tags: [convolution, tcn, numpy]
skills: [from-scratch]
packages: []
---
A **causal convolution** makes output `y[t]` from the input at time t and earlier times only.
It never looks at the future. This is the building block of a TCN (temporal convolutional network).

With a kernel `w` of length `k` and a **dilation** `d` (the gap between taps):

`y[t] = w[0]·x[t] + w[1]·x[t − d] + w[2]·x[t − 2d] + … + w[k−1]·x[t − (k−1)d]`

Values before the start of the series (index < 0) count as 0.

Write:

1. `causal_conv1d(x, w, dilation=1)` returns an array with the same length as `x`.
2. `receptive_field(kernel_size, dilations)` returns how many past steps (including the current one) the last layer can see, when you stack one layer per dilation in the list.

For stacked layers the formula is `1 + (kernel_size − 1)·(d1 + d2 + … )`.

### Example 1
**Input:** `causal_conv1d(np.array([1.,2.,3.,4.]), np.array([1.,1.]))`
**Output:** `array([1., 3., 5., 7.])`
**Explanation:** `y[t] = x[t] + x[t−1]`. At t=0, `x[−1]` is 0, so `y[0] = 1`.

### Example 2
**Input:** `receptive_field(2, [1, 2, 4, 8])`
**Output:** `16`
**Explanation:** `1 + (2−1)·(1+2+4+8) = 16`.

### Constraints
- `0 <= len(x) <= 10^5`, `1 <= len(w) <= 16`, `1 <= dilation <= 64`
- An empty `x` returns an empty array.

### Hints
1. Think of `x` padded with `(k−1)·d` zeros on the left.
2. For each tap j, add `w[j]` times the series shifted right by `j·d` positions (fill with zeros).
3. Loop over the taps (at most 16), not over time. Slice: `y[j*d:] += w[j] * x[:n - j*d]` (skip taps with `j*d >= n`).

### Solution explanation
Each tap is one shifted copy of `x`. Adding the shifted copies with weights is the whole convolution.
Time `O(n·k)`, space `O(n)`. The receptive field is a one-line formula: each layer adds `(k−1)·d` steps.
Common bug: shifting to the left (that would look into the future), or forgetting that taps past the start contribute 0.
