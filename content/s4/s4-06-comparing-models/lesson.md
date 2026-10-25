---
id: s4-06-comparing-models
title: Comparing models fairly
minutes: 30
level: advanced
goals: [Compare models on many series with average ranks and relative errors, Explain the idea of the Diebold-Mariano test, Avoid unfair comparisons such as different folds or no baseline]
prereqs: [s4-02-backtesting, s4-03-point-metrics]
tags: [evaluation, comparison, diebold-mariano, baseline]
skills: [baseline-first, metrics, backtest]
---
## Warm-up
```check
{"q": "MASE = 0.9 for your model. What does it say?", "type": "single",
 "options": ["Your model is 10% better than the in-sample naive method", "Your model has 0.9% error", "Your model is 90% accurate"],
 "answer": 0,
 "why": ["Correct: your error is 0.9 times the naive error.", "MASE is a ratio, not a percent of the actual values.", "Accuracy in percent is not what MASE measures."]}
```

```check
{"q": "Why do we use many backtest origins and not one?", "type": "single",
 "options": ["One window can be lucky or unlucky", "It makes training faster", "It removes the need for a baseline"],
 "answer": 0,
 "why": ["Correct: the average over many windows is more reliable.", "More origins mean more runs, so it is slower.", "A baseline is still needed."]}
```

## Why it matters
Model A has MAE 4.1. Model B has MAE 4.0. Is B better? Maybe. Maybe it is only noise. Maybe B was tested on easier days. Maybe it wins on 3 series and loses badly on 7. Fair comparison needs rules: **same data, same folds, same metric, a baseline, many series, and a check that the gap is not luck**. Companies lose a lot of time when they choose a model from an unfair test.

## Rule 1: same folds, and a baseline
All models must use exactly the same train/test windows, the same horizon and the same data version. Always include simple baselines: naive, seasonal naive, maybe drift. Report how much better you are than the best baseline. People call this **[[forecast value added]]** (FVA): the gain compared with a simple method. A complex model that does not beat seasonal naive adds cost and no value.

```check
{"q": "Your new deep model has MAE 12.0. Seasonal naive on the same folds has MAE 11.5. What do you do?", "type": "single",
 "options": ["Ship the deep model; it is modern", "Do not ship it yet; it is worse than a simple baseline", "Change the metric until the deep model wins"],
 "answer": 1,
 "why": ["Modern is not a reason. A baseline is better and cheaper.", "Correct: no value is added over the baseline.", "Changing the metric after seeing results is a form of cheating."]}
```

## Rule 2: many series, ranks and relative errors
With many series, one MAE per model mixes series of very different size. Two better tools.

**[[average rank|Average rank]].** For each series rank the models (1 = best). Then average the ranks per model.

Example: 3 series, models A, B, C. Ranks of A: 1, 2, 1. Average rank of A = 1.33.

**Relative error vs a baseline.** For each series divide the model error by the baseline error. Then combine with the **[[geometric mean]]** (the n-th root of the product), because ratios multiply.

Example: ratios 0.8 and 1.25 for two series. The arithmetic mean is 1.025 (looks worse). The geometric mean is sqrt(0.8 × 1.25) = 1.0 (a fair tie).

Values below 1 mean better than the baseline. The M4 competition (2018) combined two relative errors in a score called OWA.

```check
{"q": "Relative errors vs baseline on two series: 0.5 and 2.0. What is the geometric mean?", "type": "numeric",
 "answer": 1, "tol": 0.001,
 "why": "sqrt(0.5 × 2.0) = sqrt(1) = 1. On average it is as good as the baseline."}
```

## Rule 3: is the difference real? Diebold-Mariano idea
Two models have different errors on the same test points. We ask: is the difference larger than random noise?

The **[[diebold-mariano test|Diebold-Mariano (DM) test]]** looks at the loss difference at each time:

`d_t = L(e1_t) − L(e2_t)`

- `e1_t`, `e2_t` are the forecast errors of models 1 and 2 at time `t`.
- `L` is a loss, for example `L(e) = e²` or `|e|`.

If model 1 is better, `d_t` is negative on average. The test statistic is

`DM = mean(d) / sqrt(Var / n)`

- `mean(d)` is the average loss difference.
- `n` is the number of test points.
- `Var` is the variance of `d`, corrected for autocorrelation when the horizon `h > 1` (errors of multi-step forecasts are correlated).

Large `|DM|` (about 2 or more, for a 5% level) means the difference is unlikely to be luck. Use the same folds for both models. For small samples, use the Harvey correction (a small-sample fix). Keep it simple in interviews: **"it tests whether the mean loss difference is zero."**

```check
{"q": "DM statistic = 0.6 for two models. What do you conclude?", "type": "single",
 "options": ["Model 1 is clearly better", "The difference is within noise; we cannot say that one is better", "Model 2 is clearly better"],
 "answer": 1,
 "why": ["A DM value of 0.6 is small. We would need about 2.", "Correct: |DM| is far below 2, so the gap may be luck.", "The sign does not matter if |DM| is small."]}
```

## Other traps
- **[[winner's curse|Winner's curse]].** If you test 50 models and pick the best, its score is optimistic. Use a final untouched period.
- **Different data volume.** Compare on series that all models can forecast. Do not drop hard series for one model only.
- **Averages hide losers.** Show the share of series where the new model wins, and the worst 10%.
- **Cost.** Report training time, prediction time and complexity next to accuracy.

```chart
{"title": "Relative MAE of a new model vs seasonal naive (10 series)", "x": "series", "height": 220, "kind": "bar",
 "series": [{"name": "relative MAE", "kind": "bar", "y": [0.7, 0.8, 0.85, 0.9, 0.95, 0.97, 1.0, 1.05, 1.2, 1.6]}],
 "marks": [],
 "caption": "Values below 1 are wins. The mean looks fine, but two series are clearly worse. Illustration with made-up numbers."}
```

## Worked example
Six series, three models. We compute average ranks, geometric relative MAE against the naive baseline, and a simple DM statistic (horizon 1, squared error) on one series.

```python
import numpy as np
import pandas as pd

rng = np.random.default_rng(7)
# MAE per series (rows) and model (columns)
mae = pd.DataFrame({
    "naive": [10.0, 4.0, 25.0, 8.0, 3.0, 40.0],
    "model_a": [8.0, 4.4, 20.0, 7.5, 2.4, 36.0],
    "model_b": [8.5, 3.6, 21.0, 8.4, 2.8, 33.0],
}, index=[f"s{i}" for i in range(1, 7)])

avg_rank = mae.rank(axis=1).mean()                        # 1 = best, ties get average rank
rel = mae.div(mae["naive"], axis=0)                       # error / baseline error per series
geo = np.exp(np.log(rel).mean())                          # geometric mean of ratios
print(pd.DataFrame({"avg_rank": avg_rank.round(2), "geo_rel_mae": geo.round(3)}))

# Diebold-Mariano (h = 1, squared error loss) for two error series
n = 120
e_a = rng.normal(0, 2.0, n)
e_b = rng.normal(0, 1.8, n)
d = e_a ** 2 - e_b ** 2                                   # loss difference
dm = d.mean() / np.sqrt(d.var(ddof=1) / n)
print("DM statistic:", round(dm, 2))
# Output:
#          avg_rank  geo_rel_mae
# naive        2.67        1.000
# model_a      1.50        0.883
# model_b      1.83        0.897
# DM statistic: 0.32
```

Model A and model B have similar rank and relative error. The DM statistic is small, so we cannot claim that B is better than A on that series. Both models beat the naive baseline on most series.

## Common mistakes
- Comparing models on different folds or after different data cleaning.
- No baseline, or only a weak baseline such as the mean.
- Averaging raw errors over series of different scale.
- Choosing the model that wins on the test set and reporting the same test score.
- Calling a 1% gain a win without any significance check or cost analysis.
- Ignoring that errors at horizon `h > 1` are correlated when you apply the DM test.

## Interview lens
**Typical question:** "Your new model has a lower average error than the current one. How do you decide to replace it?"

**Strong answer:** First I check that both were tested on the same backtest folds and data. I compare against a simple baseline, so I can report the gain. With many series I do not average raw errors. I look at relative errors, average ranks, and the share of series that improve, plus the worst cases. To see if the gain is real I compute the loss difference per test point and run a Diebold-Mariano style test, or a bootstrap. Finally I weigh cost, latency and maintenance, and I ask for a champion-challenger test in production.

**Red flags:** "The new one is 1% lower, so it is better"; no baseline; one test window; ignoring variance; picking a metric after seeing the results.

## Real world
- The M4 competition (Makridakis et al., 2018) had 100,000 series. Results were ranked using relative scores (OWA) so that large series do not dominate. Simple methods such as Theta and combinations were hard to beat.
- The M5 competition (Walmart sales) ranked teams on a hidden period with a weighted scaled error; gradient boosting methods did very well.
- Diebold and Mariano published their test in 1995. It is still the standard way to compare two forecasts on the same data.

## Key points
- Compare on the same folds, the same horizon, the same data, with simple baselines.
- For many series use relative errors (geometric mean), average ranks and win rates, not raw sums.
- The Diebold-Mariano test checks whether the mean loss difference is different from zero.
- Beware the winner's curse. Keep a final untouched test period.
- Report cost and complexity next to accuracy.
