---
slug: sarimax-forecast
title: SARIMAX Fit, AIC Choice and Forecast
difficulty: Medium
type: function
tags: [sarimax, statsmodels, aic, seasonal]
skills: [backtest, baseline-first]
packages: [statsmodels]
companies_style: [retail demand, energy load]
---
Use `statsmodels` to fit seasonal ARIMA models. Pick the best one by AIC and forecast with it.

Write `best_sarimax(y, candidates, h)`.

- `y`: a list or array of numbers (the training series).
- `candidates`: a list of `(order, seasonal_order)` pairs. For example `((0, 1, 1), (0, 1, 1, 4))`.
- `h`: the number of steps to forecast.

For each candidate fit `SARIMAX(y, order=order, seasonal_order=seasonal_order).fit(disp=False)`. Hide all warnings. Then return a dict:

- `"best"`: the **index** in `candidates` of the model with the lowest AIC (on a tie, the lowest index).
- `"aic"`: the AIC of the best model, rounded to 1 decimal.
- `"forecast"`: the `h` forecasts of the best model (`fit.forecast(h)`), rounded to 2 decimals, as a list.

Also write `seasonal_naive(y, m, h)` that repeats the last `m` values to make `h` forecasts (as a list of floats). Use it to compare your model with the baseline.

### Example 1
**Input:** a quarterly series of 60 points with trend and yearly season (m = 4); candidates `[((1,0,0),(0,0,0,0)), ((0,1,1),(0,1,1,4))]`
**Output:** `best = 1`. The seasonal model has a much lower AIC.

### Example 2
**Input:** `seasonal_naive([1, 2, 3, 4], 2, 5)`
**Output:** `[3.0, 4.0, 3.0, 4.0, 3.0]`

### Constraints
- `len(y) >= 10 * m` for any seasonal candidate with `m > 0`
- At most 3 candidates, `h <= 12`
- Use only `statsmodels.tsa.statespace.sarimax.SARIMAX`.

### Hints
1. `from statsmodels.tsa.statespace.sarimax import SARIMAX`. The result has `.aic` and `.forecast(h)`.
2. Wrap the fits in `warnings.catch_warnings()` with `simplefilter("ignore")`.
3. For `seasonal_naive` use `y[-m:]` and index with `i % m`.

### Solution explanation
AIC trades the fit against the number of parameters. Since all candidates are fitted on the same series and the same differencing is used for equal `(d, D)`, it is fair to compare those that share `d` and `D`. The seasonal difference in the second candidate removes the yearly pattern, so its AIC is far lower. The cost is one optimiser run per candidate. Common bugs: comparing models with different `d` (the AIC is not comparable), forgetting `disp=False`, and returning the model object instead of numbers.
