---
slug: rnn-cell-forward
title: One Step of a Recurrent Cell
difficulty: Easy
type: function
tags: [rnn, numpy, deep-learning]
skills: [from-scratch]
packages: []
---
A **recurrent cell** reads one value at a time and keeps a memory called the **hidden state**.
At each step it mixes the new input with the old memory:

`h(t) = tanh( x(t)·Wxh + h(t−1)·Whh + b )`

- `x(t)` is the input at time t, a vector with `F` numbers.
- `h(t−1)` is the old hidden state, a vector with `H` numbers.
- `Wxh` has shape `[F, H]`, `Whh` has shape `[H, H]`, `b` has shape `[H]`.

Write two functions:

1. `rnn_step(x, h, Wxh, Whh, b)` returns the new hidden state (shape `[H]`).
2. `rnn_forward(X, Wxh, Whh, b)` reads a whole sequence `X` with shape `[T, F]`, starts from `h = zeros(H)`, and returns all hidden states with shape `[T, H]`.

### Example 1
**Input:** `rnn_step(np.array([1.0]), np.array([0.0]), np.array([[0.5]]), np.array([[0.9]]), np.array([0.0]))`
**Output:** `array([0.46211716])`
**Explanation:** `tanh(1·0.5 + 0·0.9 + 0) = tanh(0.5) = 0.46211716`.

### Example 2
**Input:** `rnn_forward` on `X = [[1],[1]]` with the same weights.
**Output:** `[[0.46211716],[0.72395463]]`
**Explanation:** The second step also uses the first state: `tanh(0.5 + 0.46211716·0.9) ≈ 0.7240`.

### Constraints
- `0 <= T <= 1000`, `1 <= F, H <= 64`
- If `T = 0`, return an array with shape `[0, H]`.

### Hints
1. `x @ Wxh` is a matrix product. A vector of length F times `[F, H]` gives a vector of length H.
2. Use `np.tanh`.
3. In `rnn_forward`, keep one variable `h`, update it in a loop over time, and collect each new `h` in a list.

### Solution explanation
`rnn_step` is one line. `rnn_forward` loops over time because step t needs the answer of step t−1.
That dependency is why RNNs cannot be computed in parallel over time.
Time `O(T·(F·H + H²))`, memory `O(T·H)` for the saved states.
Common bug: starting `h` from the wrong shape, or using `*` instead of `@`.
