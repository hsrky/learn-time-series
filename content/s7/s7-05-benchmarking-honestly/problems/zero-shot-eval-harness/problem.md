---
slug: zero-shot-eval-harness
title: Fair Zero-Shot Evaluation Harness
difficulty: Hard
type: function
tags: [benchmark, mase, foundation-models, evaluation]
skills: [metrics, baseline-first, backtest]
packages: []
companies_style: [model selection, forecasting platform]
---
You compare several forecasting models on many series. A fair report uses a **scale-free** error and a
**baseline**. Here you build the small harness that many benchmarks (such as GIFT-Eval and fev-bench) use in a similar way.

For each series you get a `train` array (the history) and a `test` array (the next `horizon` values).
`forecasts[name][i]` is the forecast of model `name` for series `i` (length `horizon`).

Write `evaluate_models(train_list, test_list, forecasts, season)`:

1. **MASE** of a forecast = `mean(|test − forecast|) / scale`, where `scale = mean(|train[t] − train[t−season]|)` over the training data.
2. The **seasonal naive** baseline repeats the last `season` training values to fill the horizon (cycle them if the horizon is longer than `season`).
3. For each model and series: `rel = MASE_model / MASE_seasonal_naive`.
4. **Skip a series** if `len(train) <= season`, or `scale == 0`, or the seasonal naive MASE is 0.
5. Return a dict `{name: {"mase": arithmetic mean of MASE over kept series, "rel_mase": geometric mean of rel over kept series}}` for every model name in `forecasts`, **plus** the key `"seasonal_naive"` (its `rel_mase` is 1.0).
6. If no series is kept, all numbers are `nan`.

The **geometric mean** is `exp(mean(log(rel)))`. It is the right average for ratios: a model that is 2x better on one series and 2x worse on another is "equal" (1.0), not worse.

### Example 1
**Input:** one series `train=[1,2,3,2,3,4]`, `test=[3,3,5]`, `season=3`, and a model with forecast `[3,3,4]`.
**Output:** `seasonal_naive` has `mase = 0.6667` and `rel_mase = 1.0`; the model has `mase = 0.3333` and `rel_mase = 0.5`.
**Explanation:** The scale is the mean of `|train[t] − train[t−3]|` = mean(1, 1, 1) = 1. Seasonal naive forecasts `[2,3,4]`, so its errors are 1, 0, 1 and its MASE is 2/3.
The model errors are 0, 0, 1, so its MASE is 1/3. The ratio is 0.5: the model is twice as good as the baseline.

### Constraints
- Up to 1000 series, horizon up to 100, `season >= 1`.
- Forecasts and arrays contain no NaN.

### Hints
1. Write a helper `mase(test, fc, train, season)`; the denominator is `np.mean(np.abs(train[season:] - train[:-season]))`.
2. Seasonal naive: `np.resize(train[-season:], horizon)` repeats the last season to the right length.
3. Collect `rel` values in lists per model, then `np.exp(np.mean(np.log(rels)))`. If a model has `rel = 0` (perfect forecast), the log breaks: clip `rel` at `1e-12`.

### Solution explanation
Dividing by the seasonal naive MASE shows "how many times better or worse than a free baseline". A number below 1 means the model adds value.
The geometric mean stops one series with a huge ratio from dominating. Always report the baseline: a model that is not below 1.0 is not worth its cost.
Time `O(models · series · horizon)`. Common bugs: arithmetic mean of ratios, scaling with the test data (leakage), and forgetting to skip degenerate series.
