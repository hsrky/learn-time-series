---
slug: ma-invertibility
title: Is the MA Model Invertible?
difficulty: Easy
type: function
tags: [ma, invertibility, polynomial-roots]
skills: [from-scratch]
packages: []
companies_style: [forecasting interview]
---
An MA(q) model with coefficients `theta = [theta1, ..., thetaq]` is **invertible** when all the roots of the polynomial

`1 + theta1 * z + theta2 * z^2 + ... + thetaq * z^q`

have an absolute value **greater than 1** (they lie outside the unit circle). The same test with `1 - phi1*z - ... - phip*z^p` tells you if an AR model is **stationary**.

Write two functions:

1. `ma_invertible(theta)` returns `True` or `False` for an MA model.
2. `ar_stationary(phi)` returns `True` or `False` for an AR model.

Use `np.roots`. Treat a root with absolute value `<= 1 + 1e-9` as **inside** (not allowed). An empty list means white noise: return `True` for both.

Trim zeros at the end of the list before you build the polynomial (for example `[0.5, 0]` is the same as `[0.5]`).

### Example 1
**Input:** `ma_invertible([0.5])`
**Output:** `True`
**Explanation:** `1 + 0.5 z = 0` gives `z = -2`, and `|-2| > 1`.

### Example 2
**Input:** `ma_invertible([2.0])`
**Output:** `False`
**Explanation:** The root is `z = -0.5`, which is inside the unit circle.

### Example 3
**Input:** `ar_stationary([0.6, 0.3])`
**Output:** `True`. The AR(2) roots of `1 - 0.6 z - 0.3 z^2` have absolute values larger than 1.

### Constraints
- `0 <= len(theta), len(phi) <= 10`
- Coefficients are floats.

### Hints
1. `np.roots` expects coefficients from the **highest** power to the lowest. Reverse your list.
2. For MA the coefficients are `[1, theta1, ..., thetaq]` in increasing power. For AR they are `[1, -phi1, ..., -phip]`.
3. Use `np.abs(roots) > 1 + 1e-9` and `np.all`.

### Solution explanation
The invertibility and stationarity conditions are the same type of statement about the roots of a polynomial. Build the polynomial, find the roots with `np.roots` (eigenvalues of a small companion matrix), and compare their absolute values with 1. Time is O(q^3) for the eigenvalues, tiny for q <= 10. Common bugs: not reversing the coefficients, using the wrong sign for the AR polynomial, and forgetting to trim trailing zeros (which would add a root at infinity).
