---
slug: unit-root-verdict
title: Unit-Root Verdict with ADF and KPSS
difficulty: Medium
type: function
tags: [adf, kpss, statsmodels, stationarity]
skills: [from-scratch]
packages: [statsmodels]
companies_style: [forecasting take-home]
---
Use `statsmodels` to combine the ADF and KPSS tests, as in the lesson.

Write `unit_root_verdict(x, alpha=0.05)`. It returns a dict:

- `"adf_p"`: the p-value of `adfuller(x, regression="c", autolag="AIC")`, rounded to 4 decimals.
- `"kpss_p"`: the p-value of `kpss(x, regression="c", nlags="auto")`, rounded to 4 decimals.
- `"verdict"`: one of
  - `"stationary"`: ADF p < alpha **and** KPSS p >= alpha.
  - `"unit root"`: ADF p >= alpha **and** KPSS p < alpha.
  - `"mixed"`: both tests reject (ADF p < alpha and KPSS p < alpha).
  - `"inconclusive"`: neither test rejects.

Write also `suggest_d(x, max_d=2, alpha=0.05)`. It returns the smallest `d` in `0..max_d` such that the series, after `d` first differences (`np.diff`), has the verdict `"stationary"`. If no `d` works, return `max_d`.

Remember: the two tests have **opposite** null hypotheses. Hide the KPSS interpolation warning with the `warnings` module.

### Example 1
**Input:** a random walk of 300 points (seed 0).
**Output:** `verdict = "unit root"`, and `suggest_d(...) = 1`.
**Explanation:** ADF p is large (0.84) and KPSS p is small (0.01). After one difference the series is white noise.

### Example 2
**Input:** a stationary AR(1) series with phi = 0.5.
**Output:** `verdict = "stationary"`, and `suggest_d(...) = 0`.

### Constraints
- `len(x) >= 30`
- `x` is a list or numpy array of floats.
- Round p-values with `round(p, 4)`.

### Hints
1. Import `adfuller` and `kpss` from `statsmodels.tsa.stattools`. The p-value is the second item of each result.
2. Write the verdict with two booleans: `adf_rejects = adf_p < alpha` and `kpss_rejects = kpss_p < alpha`.
3. For `suggest_d`, loop over `d` and apply `np.diff` before each test.

### Solution explanation
The ADF null is "unit root", so a small p means stationary. The KPSS null is "stationary", so a small p means not stationary. A table of the four combinations gives the verdict. `suggest_d` repeats the test on differenced data and stops at the first stationary result. Cost: a few regressions, about O(n * lags) each. Common bugs: reading KPSS like ADF, forgetting `nlags="auto"` so a warning about lags appears, and not suppressing the warning.
