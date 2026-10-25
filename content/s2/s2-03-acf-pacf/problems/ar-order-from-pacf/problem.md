---
slug: ar-order-from-pacf
title: Guess the AR and MA Order
difficulty: Easy
type: function
tags: [acf, pacf, order-selection]
skills: [from-scratch]
packages: []
companies_style: [forecasting interview]
---
You have the sample [[ACF]] and [[PACF]] of a stationary series with `n` points. Use the rule of thumb from the lesson:

- The 95% band is `1.96 / sqrt(n)`. A value is **significant** if its absolute value is **greater than** the band.
- `p` = the largest lag `k >= 1` where the PACF is significant (0 if none).
- `q` = the largest lag `k >= 1` where the ACF is significant (0 if none).

Write `suggest_orders(acf_vals, pacf_vals, n)`. Both lists start with lag 0 (the value 1.0). Look only at lags 1 and above. Return a dict with the keys `"p"`, `"q"` and `"model"`. Choose `"model"` with these rules, in this order:

1. `p == 0` and `q == 0`: `"white noise"`.
2. `q == 0`: `"AR(p)"`, with the real number, for example `"AR(2)"`.
3. `p == 0`: `"MA(q)"`, for example `"MA(1)"`.
4. `p < q` (the PACF cuts off sooner): `"AR(p)"`.
5. `q < p` (the ACF cuts off sooner): `"MA(q)"`.
6. Otherwise (`p == q`): `"ARMA"`.

### Example 1
**Input:** `acf_vals = [1, 0.7, 0.5, 0.3, 0.1]`, `pacf_vals = [1, 0.7, 0.05, 0.02, 0.0]`, `n = 100`
**Output:** `{"p": 1, "q": 3, "model": "AR(1)"}`
**Explanation:** The band is 0.196. The ACF is significant at lags 1, 2, 3. The PACF only at lag 1. The PACF cuts off sooner, so the model is AR(1).

### Example 2
**Input:** `acf_vals = [1, 0.1, 0.05]`, `pacf_vals = [1, 0.1, 0.05]`, `n = 100`
**Output:** `{"p": 0, "q": 0, "model": "white noise"}`

### Constraints
- `len(acf_vals) == len(pacf_vals) >= 2`
- `n >= 4`
- Compare with strict greater-than (a value equal to the band is not significant).

### Hints
1. Compute `band = 1.96 / np.sqrt(n)`.
2. Use `np.abs(arr[1:]) > band` and find the last `True` with `np.nonzero`.
3. Add 1 to the index because you skipped lag 0.

### Solution explanation
Two scans, one per array. A helper returns the last significant lag. Then the model name follows from p and q. Time O(L) where L is the number of lags. This is only a rule of thumb. In practice you also compare AIC values and check the residuals.
