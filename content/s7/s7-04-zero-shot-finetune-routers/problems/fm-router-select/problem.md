---
slug: fm-router-select
title: Per-Series Model Router
difficulty: Medium
type: function
tags: [model-selection, routing, foundation-models]
skills: [baseline-first, backtest, scale]
packages: []
---
You have `M` models (for example seasonal naive, LightGBM, two foundation models) and `S` series.
A **router** picks one model for each series, using errors measured on a **validation** period.
You then check the router on a later **test** period. This shows if "pick the best model per series" really helps.

Write `route(val_err, test_err)`:

- `val_err` and `test_err` are arrays with shape `[M, S]`: the error of model `m` on series `s` (lower is better).
- For each series, choose the model with the lowest `val_err` (if models tie, choose the lowest index).
- Also find the single **global best** model: the lowest mean `val_err` over all series (ties: lowest index).
- Return a dict:
  - `"choice"`: list of `S` model indexes chosen by the router.
  - `"global"`: index of the global best model.
  - `"router_test"`: mean over series of the router's `test_err`.
  - `"global_test"`: mean over series of the global best model's `test_err`.

### Example 1
**Input:** `val_err = [[1, 5], [2, 1]]`, `test_err = [[1, 5], [2, 1]]`
**Output:** `{"choice": [0, 1], "global": 1, "router_test": 1.0, "global_test": 1.5}`
**Explanation:** Series 0 is best with model 0 (error 1), series 1 with model 1 (error 1). The mean validation errors are 3.0 (model 0) and 1.5 (model 1), so the global best is model 1.
The router has mean test error (1 + 1) / 2 = 1.0. The global best has (2 + 1) / 2 = 1.5.

### Constraints
- `1 <= M <= 20`, `0 <= S <= 10^5`. If `S = 0`, return `choice = []`, `global = 0`, and both test numbers `0.0`.

### Hints
1. `np.argmin(val_err, axis=0)` returns the first minimum, which handles ties.
2. `np.argmin(val_err.mean(axis=1))` is the global best.
3. Pick router errors with `test_err[choice, np.arange(S)]`.

### Solution explanation
The router can overfit: with many models and noisy validation errors, the model that looks best on validation is often just lucky.
So the router's test error can be worse than the global best. Real systems keep the choice simple, use long validation windows, or average several models instead.
Time `O(M·S)`.
