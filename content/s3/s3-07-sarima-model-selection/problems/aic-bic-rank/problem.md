---
slug: aic-bic-rank
title: Rank Models by AIC and BIC
difficulty: Easy
type: function
tags: [aic, bic, model-selection]
skills: [from-scratch, backtest]
packages: []
companies_style: [forecasting interview]
---
For a model with Gaussian errors, the information criteria can be computed from the sum of squared residuals `sse`, the number of observations `n` and the number of parameters `k`:

- `AIC = n * ln(sse / n) + 2 * k`
- `BIC = n * ln(sse / n) + k * ln(n)`

(The constant terms that are equal for all models are dropped.) **Lower is better.**

Write `rank_models(models, n, criterion="aic")`.

- `models` is a dict `{name: (sse, k)}`.
- Return a list of `(name, score)` pairs sorted from best (lowest) to worst, with `score` rounded to 4 decimals.
- Break ties by the model name (alphabetical).
- `criterion` is `"aic"` or `"bic"`. Raise `ValueError` for any other value.

### Example 1
**Input:** `rank_models({"AR1": (120.0, 2), "AR3": (100.0, 4), "AR8": (95.0, 9)}, 50, "aic")`
**Output:** `[("AR3", 42.6574), ("AR1", 47.7734), ("AR8", 50.0927)]`
**Explanation:** AR3 has the best balance of error and size.

### Example 2
**Input:** the same models with `"bic"`
**Output:** `[("AR3", 50.3055), ("AR1", 51.5975), ("AR8", 67.3009)]`
**Explanation:** BIC punishes the 9 parameters of AR8 much more than AIC does.

### Constraints
- `1 <= len(models) <= 50`, `sse > 0`, `n >= 2`, `k >= 1`

### Hints
1. Write a small function `score(sse, k)` for the chosen criterion.
2. Build `[(name, score)]` and sort with the key `(score, name)`.
3. Round at the end, not before sorting.

### Solution explanation
The first term rewards a small error. The second term is a penalty on complexity: `2k` for AIC and `k ln(n)` for BIC. Since `ln(n) > 2` when n is above about 7.4, BIC punishes extra parameters more. Time O(m log m) for m models. Common bugs: using log base 10, dividing by the wrong n, and sorting from high to low.
