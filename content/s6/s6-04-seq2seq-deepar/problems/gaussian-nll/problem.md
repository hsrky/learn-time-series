---
slug: gaussian-nll
title: Gaussian Negative Log-Likelihood (DeepAR Loss)
difficulty: Easy
type: function
tags: [probabilistic, deepar, loss]
skills: [uncertainty, from-scratch]
packages: []
---
DeepAR does not predict one number. At each step it predicts a **mean** `mu` and a **spread** `sigma`
of a normal distribution. To train it, you score how likely the real value `y` is under that
distribution. The loss is the **negative log-likelihood** (NLL). Lower is better.

For one point:

`NLL = 0.5·log(2π·σ²) + (y − μ)² / (2σ²)`

Write `gaussian_nll(y, mu, sigma, mask=None)`:

- `y`, `mu`, `sigma` are numpy arrays of the same shape (any shape). `sigma > 0`.
- `mask` (optional) has the same shape, with 1 for real points and 0 for padding. Padded points are ignored.
- Return the **mean** NLL over the points where `mask == 1` (all points if `mask` is `None`).
- If no point is kept, return `0.0`.

### Example 1
**Input:** `gaussian_nll(np.array([0.0]), np.array([0.0]), np.array([1.0]))`
**Output:** `0.9189385...`
**Explanation:** `0.5·log(2π) = 0.9189`. The error is 0, so the second term is 0.

### Example 2
**Input:** `gaussian_nll(np.array([2.0]), np.array([0.0]), np.array([1.0]))`
**Output:** `2.9189385...`
**Explanation:** The extra term is `2² / 2 = 2`.

### Constraints
- Up to `10^6` points.
- Use numpy only (no scipy).

### Hints
1. Write the per-point formula with numpy operations on whole arrays.
2. `np.log` and `np.pi` are enough.
3. For the mask: `np.sum(nll * mask) / np.sum(mask)`; check for `sum(mask) == 0` first.

### Solution explanation
A small `sigma` is rewarded when the error is small and punished hard when the error is big.
So the model learns honest uncertainty. The `log σ` term stops the model from always choosing a huge sigma.
Time `O(n)`, space `O(n)`. Common bug: using `sigma` where the formula needs `sigma²`.
