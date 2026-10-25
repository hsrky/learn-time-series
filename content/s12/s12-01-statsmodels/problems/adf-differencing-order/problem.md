---
slug: adf-differencing-order
title: How Many Differences? (ADF Test)
difficulty: Medium
type: function
tags: [statsmodels, adfuller, stationarity, differencing]
skills: [stationarity, statsmodels]
packages: [statsmodels]
companies_style: [forecasting pipeline, ARIMA preparation]
---
ARIMA needs a **stationary** series. A simple automatic rule is: difference the series until the **Augmented Dickey-Fuller (ADF) test** says it is stationary. The number of differences is the `d` in ARIMA(p, d, q).

Write `differencing_order(y, alpha=0.05, max_d=2)`.

Start with `x = y` and `d = 0`. Repeat:

1. If `x` has fewer than 10 values or is constant (all values equal), return `d`.
2. Run `statsmodels.tsa.stattools.adfuller(x, autolag="AIC")`. Take the p-value (second item of the result).
3. If the p-value is **smaller than `alpha`**, the series is stationary: return `d`.
4. If `d == max_d`, return `max_d`. Otherwise set `x = np.diff(x)` and `d = d + 1`.

### Example 1
**Input:** a random walk (cumulative sum of white noise)
**Output:** `1`
**Explanation:** A random walk is not stationary. Its first difference is white noise, which is stationary.

### Example 2
**Input:** white noise
**Output:** `0`

### Constraints
- 1 ≤ length ≤ 5 000. Values are finite floats.
- `alpha` is between 0 and 1. `0 ≤ max_d ≤ 3`.

### Hints
1. `from statsmodels.tsa.stattools import adfuller`. The result is a tuple; the p-value is `result[1]`.
2. Use a loop with `np.diff` to difference again.
3. Handle the stop rules first: constant series (`np.ptp(x) == 0`) or fewer than 10 values.

### Solution explanation
The ADF test has the null hypothesis "the series has a unit root" (it is non-stationary). A small p-value rejects it. Differencing removes a unit root, so we test, difference, and test again. We stop at `max_d` to avoid over-differencing. Complexity: one ADF test per level, so O(max_d · n · lags). Common bugs: calling `adfuller` on a constant series (it raises an error), comparing the test statistic instead of the p-value, and differencing one time too many after the series is already stationary.
