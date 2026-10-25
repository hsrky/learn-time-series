---
slug: ar-recursive-forecast
title: Recursive AR Forecast
difficulty: Medium
type: function
tags: [ar, recursive-forecast, multi-step]
skills: [from-scratch, leakage]
packages: []
companies_style: [forecasting take-home]
---
You have the fitted coefficients of an AR(p) model and the history of the series. Produce a multi-step forecast with the **recursive** method.

Write `ar_forecast(y, coefs, h)`.

- `coefs = [c, phi1, ..., phip]`, so `p = len(coefs) - 1`.
- The forecast for the next step is `c + phi1 * y[-1] + phi2 * y[-2] + ... + phip * y[-p]`.
- After each step, append the **forecast** (not any real value) to the history and repeat.

Return a numpy array of `h` forecasts. If `len(y) < p`, raise `ValueError`.

### Example 1
**Input:** `ar_forecast([8, 9, 10], [2.0, 0.8], 3)`
**Output:** `array([10., 10., 10.])`
**Explanation:** The mean of the model is 2 / (1 - 0.8) = 10. The last value is 10, so every forecast stays at 10.

### Example 2
**Input:** `ar_forecast([15], [2.0, 0.8], 3)`
**Output:** `array([14., 13.2, 12.56])`
**Explanation:** 2 + 0.8 * 15 = 14, then 2 + 0.8 * 14 = 13.2, then 2 + 0.8 * 13.2 = 12.56.

### Constraints
- `1 <= p <= 20`, `0 <= h <= 1000`, `len(y) >= p`
- Do not change the input list.

### Hints
1. Copy the history into a Python list and work on the copy.
2. The last p values in reverse order are `hist[-1:-p-1:-1]`, which matches `phi1 ... phip`.
3. Append the new forecast to the history inside the loop.

### Solution explanation
At each step the lags come from the history, which now holds earlier forecasts. This feeds the model its own output. Time O(h * p). For a stationary model the forecasts approach the model mean `c / (1 - sum(phi))`. Common bugs: using the lags in the wrong order, modifying the caller's list, and using true future values (leakage).
