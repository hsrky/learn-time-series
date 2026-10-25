---
slug: ols-reconcile
title: OLS Forecast Reconciliation
difficulty: Hard
type: function
tags: [hierarchical, reconciliation, mint, linear-algebra]
skills: [from-scratch, scale]
packages: []
companies_style: [retail demand, enterprise planning]
---
You have base forecasts for **all** series of a hierarchy, and they do not add up. Make them coherent with OLS reconciliation, the simplest case of the MinT idea (the weight matrix W is the identity).

Write `ols_reconcile(S, y_hat)`.

- `S`: the summing matrix, shape `(n, m)`. Row `i` shows which bottom series build series `i`. The last `m` rows are the identity (the bottom series).
- `y_hat`: base forecasts of all `n` series (a 1D list).

Compute `b = (S^T S)^(-1) S^T y_hat` and return a dict:

- `"bottom"`: the reconciled bottom forecasts `b` (length `m`).
- `"all"`: the reconciled forecasts of all series `S @ b` (length `n`).

Also write `is_coherent(S, y, tol=1e-9)`. It returns `True` if `y` equals `S @ y_bottom` where `y_bottom` is the last `m` entries of `y` (that is, every aggregate equals the sum of its bottom series).

Use `np.linalg.solve` (not an explicit inverse).

### Example 1
**Input:** `S = [[1, 1], [1, 0], [0, 1]]`, `y_hat = [52, 31, 19]`
**Output:** `{"bottom": [31.6667, 19.6667], "all": [51.3333, 31.6667, 19.6667]}` (rounded)
**Explanation:** `S^T S = [[2, 1], [1, 2]]` and `S^T y_hat = [83, 71]`. The solution is `[95/3, 59/3]`.

### Example 2
**Input:** a `y_hat` that is already coherent, for example `[50, 30, 20]`
**Output:** `bottom = [30, 20]` and `all = [50, 30, 20]`. Nothing changes.

### Constraints
- `1 <= m <= 100`, `n >= m`, `S` has full column rank.
- Return plain Python lists of floats.

### Hints
1. `StS = S.T @ S` and `Sty = S.T @ y_hat`.
2. `np.linalg.solve(StS, Sty)` gives `b`.
3. For `is_coherent` compare `y` with `S @ y[-m:]` using `np.allclose`.

### Solution explanation
OLS finds the coherent vector that is closest (in the squared-error sense) to the base forecasts. Because coherent vectors are `S b`, this is a plain least-squares problem: choose `b` to minimise `|| y_hat - S b ||^2`. The solution is the normal equation. All base forecasts, also the aggregates, contribute to the new bottom forecasts. Time O(n m^2 + m^3). Common bugs: using the explicit inverse (less stable), forgetting the transpose, and returning only the bottom forecasts. MinT replaces the identity by an estimate of the error covariance.
