---
slug: model-rank-comparison
title: Average Rank and Relative Error Table
difficulty: Medium
type: function
tags: [pandas, comparison, ranks, m-competition]
skills: [baseline-first, metrics, pandas-fluency]
packages: []
---
You have an error table `errors`: one row per time series, one column per model, each cell is the error (for example MAE) of that model on that series. Smaller is better.

Write `compare_models(errors, baseline)` that returns a `DataFrame` indexed by model name (same order as the columns) with two columns:

- `"avg_rank"`: for each series rank the models (1 = smallest error, ties get the **average** rank), then take the mean over series.
- `"rel_error"`: for each series divide the model error by the `baseline` model's error, then take the **geometric mean** over series. Skip series where the baseline error is 0 or `NaN`, and skip `NaN` ratios.

If a model has a `NaN` error in a series, that series gets no rank for that model, and ranks of the others are computed among the models that have a value (`NaN` stays `NaN` and is ignored in the mean).

### Example 1
**Input:** `errors`:

| series | naive | A | B |
|---|---|---|---|
| s1 | 10 | 8 | 9 |
| s2 | 4 | 4 | 3 |

`baseline="naive"`

**Output:**

| model | avg_rank | rel_error |
|---|---|---|
| naive | 2.75 | 1.0 |
| A | 1.75 | 0.8944 |
| B | 1.5 | 0.8216 |

(values rounded to 4 decimals)

**Explanation:** s1 ranks: A=1, B=2, naive=3. s2: B=1, naive and A tie for ranks 2 and 3, so each gets 2.5. A: (1+2.5)/2 = 1.75. B: (2+1)/2 = 1.5. naive: (3+2.5)/2 = 2.75. Relative errors for A: 0.8 and 1.0, geometric mean = sqrt(0.8) = 0.8944. For B: 0.9 and 0.75, sqrt(0.675) = 0.8216.

### Constraints
- 1 ≤ number of series ≤ 10^4, 1 ≤ number of models ≤ 50. Errors are ≥ 0 or `NaN`.

### Hints
1. `errors.rank(axis=1)` ranks inside each row and uses average ranks for ties by default.
2. `errors.div(errors[baseline], axis=0)` gives the ratios. Replace `inf` and `NaN` rows from zero baselines.
3. Geometric mean = `np.exp(np.log(ratio).mean())`. Zero ratios give `-inf`; think about what a model with zero error should do (keep it: the geometric mean becomes 0).

### Solution explanation
Row-wise `rank` handles ties and `NaN`. For the ratios, drop series whose baseline is 0/`NaN` first, then take the mean of logs and exponentiate. Time O(S × M log M). Common bug: using the arithmetic mean of ratios, which is biased.
