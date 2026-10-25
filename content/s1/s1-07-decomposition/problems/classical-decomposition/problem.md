---
slug: classical-decomposition
title: Classical Decomposition From Scratch
difficulty: Hard
type: function
tags: [numpy, pandas, decomposition, seasonality, from-scratch]
skills: [from-scratch, pandas-fluency]
packages: []
companies_style: [demand forecasting, analytics]
---
Implement the **classical decomposition** of a series into trend, seasonal part and remainder. Do not use `statsmodels`.

Write `classical_decompose(s, period, model="additive")`. `s` is a pandas Series (regular index, no NaN). It returns a DataFrame with the same index and the columns `trend`, `seasonal`, `resid`.

**Step 1: trend.** Use a centered moving average of length `period`.

- If `period` is odd: at time t, the mean of the `period` values centered on t.
- If `period` is even: use the "2 × period" average. It is the mean of the values from t − period/2 to t + period/2 where the two end values have **half weight**: `(0.5·y[t−m/2] + y[t−m/2+1] + ... + y[t+m/2−1] + 0.5·y[t+m/2]) / m`.
- The first and last `period // 2` values of the trend are `NaN`.

**Step 2: detrend.** Additive: `y − trend`. Multiplicative: `y / trend`.

**Step 3: seasonal.** For each position `j = 0 .. period−1` take the mean of the detrended values at positions `j, j + period, j + 2·period, ...` (skip NaN). Position 0 is the **first observation** of `s`. Then center these `period` numbers: additive → subtract their mean (they now sum to 0); multiplicative → divide by their mean (their mean is now 1). Repeat them along the series.

**Step 4: remainder.** Additive: `y − trend − seasonal`. Multiplicative: `y / (trend · seasonal)`.

### Example 1
**Input:** `s = [1, 3, 1, 3, 1, 3]`, `period = 2`, `model = "additive"`
**Output:** trend `[NaN, 2, 2, 2, 2, NaN]`, seasonal `[-1, 1, -1, 1, -1, 1]`, resid `[NaN, 0, 0, 0, 0, NaN]`
**Explanation:** For `period = 2`, the weights are `[0.5, 1, 0.5] / 2`. At t = 1: `(0.5·1 + 3 + 0.5·1) / 2 = 2`. The detrended values at positions 1, 2, 3, 4 are `1, -1, 1, -1`. Position 0 averages `-1`, position 1 averages `1`. Their mean is 0, so centering changes nothing.

### Constraints
- `2 <= period` and `len(s) >= 2 * period`.
- `model` is `"additive"` or `"multiplicative"`. For multiplicative, all values are positive.
- Your result must match the textbook method (and `statsmodels.tsa.seasonal.seasonal_decompose`) to 1e-6.

### Hints
1. Build the weight vector first: all `1/m` for odd `m`; `[0.5, 1, ..., 1, 0.5] / m` for even `m`. The trend is the dot product of the weights with a sliding window. `np.convolve(y, w, mode="valid")` does this for all windows at once.
2. The trend array is shorter than `y` by `len(w) − 1`. Put it into an array of NaN, starting at index `len(w) // 2`.
3. `detrended[j::m]` is every m-th value starting at `j`. Use `np.nanmean`. Centering the seasonal indexes is a separate step: do not forget it.

### Solution explanation
1. Weights: odd `m` → `ones(m)/m`; even `m` → `[0.5, 1…1, 0.5]/m` (length `m + 1`). The window half width is `len(w) // 2`, which equals `m // 2` in both cases.
2. `np.convolve(..., "valid")` gives the trend where the full window fits. The edges stay NaN.
3. Seasonal indexes are the average detrended value per position. Centering makes them sum to 0 (additive) or average 1 (multiplicative). Otherwise, the trend and the seasonal part would both contain a constant level.
4. The remainder is what is left. For a good decomposition it looks like noise.

Time O(n), space O(n). Typical bugs: forgetting the half weights for an even period (the trend is then shifted by half a step); forgetting to center the seasonal part; starting the season at position 0 of the *calendar* instead of the first observation.

Because the trend uses values after time t, this decomposition is for **describing** a series. Do not use its parts as forecasting features without care.
