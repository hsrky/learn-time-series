---
slug: box-cox-transform
title: Box-Cox Transform and Inverse
difficulty: Easy
type: function
tags: [box-cox, log, transforms]
skills: [from-scratch]
packages: []
companies_style: [demand forecasting]
---
Implement the [[Box-Cox]] transform and its inverse with numpy. Do not use scipy.

`box_cox(y, lam)` returns, for each value `y` (all must be positive):

- `(y ** lam - 1) / lam` if `lam != 0`
- `ln(y)` if `lam == 0`

`inv_box_cox(w, lam)` undoes it:

- `(lam * w + 1) ** (1 / lam)` if `lam != 0`
- `exp(w)` if `lam == 0`

Both take a list or array and return a numpy array of floats. If any value in `y` is zero or negative, `box_cox` must raise `ValueError`.

### Example 1
**Input:** `box_cox([1, 4, 9], 0.5)`
**Output:** `array([0., 2., 4.])`
**Explanation:** For y = 9: (9^0.5 - 1) / 0.5 = (3 - 1) / 0.5 = 4.

### Example 2
**Input:** `box_cox([1, np.e], 0)`
**Output:** `array([0., 1.])`
**Explanation:** With lambda = 0 the transform is the natural log.

### Constraints
- `1 <= len(y) <= 10^5`
- `-2 <= lam <= 2`
- `inv_box_cox(box_cox(y, lam), lam)` must give back `y` (within 1e-9 relative).

### Hints
1. Convert the input with `np.asarray(y, dtype=float)`.
2. Check `np.any(y <= 0)` first and raise `ValueError`.
3. Use `if lam == 0:` for the log branch. For other `lam` use the formula directly.

### Solution explanation
The Box-Cox family is continuous at lam = 0: when lam goes to 0, (y^lam - 1) / lam goes to ln(y). So the log case is a special branch, because the formula would divide by zero. Both functions are vectorized, so time is O(n) and space O(n). Common bugs: dividing by zero at lam = 0, and forgetting the positive check.
