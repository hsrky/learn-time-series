---
id: s7-05-benchmarking-honestly
title: Benchmarking honestly (GIFT-Eval, fev-bench, leakage)
minutes: 35
level: advanced
goals: [Score models with a scale-free metric relative to seasonal naive, Aggregate scores with the geometric mean, Spot leakage and weak claims in leaderboards and vendor reports]
prereqs: [s7-04-zero-shot-finetune-routers]
tags: [benchmark, gift-eval, fev-bench, leakage, mase, 2026-trend]
skills: [metrics, leakage, backtest, communication]
---
## Warm-up

```check
{"q": "MASE divides the forecast error by:", "type": "single",
 "options": ["The in-sample error of a (seasonal) naive forecast", "The mean of the forecast", "The number of series"], "answer": 0,
 "why": ["Correct: it is a scale-free error relative to a naive baseline.", "That would be a different metric.", "Not used."]}
```

```check
{"q": "The pinball loss at quantile 0.5 equals:", "type": "single",
 "options": ["Half of the absolute error", "The squared error", "Zero"], "answer": 0,
 "why": ["Correct: max(0.5·e, −0.5·e) = 0.5·|e|.", "No.", "No."]}
```

## Why it matters

Every new model comes with a chart that says "we are the best". Your job as an engineer is to decide if that is true **for you**. Foundation models make this harder:

- they were trained on huge data sets that may include the test data,
- many benchmarks are public and used again and again,
- the leaderboard changes every month, and
- numbers in a vendor blog are chosen by the vendor.

**2026 trend:** benchmark design (not only model design) is a hot interview topic for senior roles.

## Metrics for many series

You cannot average raw errors across series: one series with big numbers would dominate. Use scale-free metrics and compare with a baseline.

- **MASE** (point forecast): error divided by the in-sample error of seasonal naive.
- **WQL** (probabilistic) is the weighted quantile loss. It is built from the pinball loss over several quantile levels:
  `WQL = mean over q of [ 2·sum of pinball / sum of |y| ]`.
- **Relative to seasonal naive:** divide the model's metric by the baseline's metric on the same series. A value of 0.8 means 20% lower error than the baseline.

Aggregate the ratios with the **geometric mean**: `exp( mean( log(ratio) ) )`. Why? A model may be twice as good on one series (ratio 0.5) and twice as bad on another (ratio 2.0). It should count as "equal" to the baseline. The geometric mean gives exactly 1.0. The arithmetic mean gives 1.25, which is unfair.

```check
{"q": "A model has ratios 0.5 and 2.0 against seasonal naive on two series. What is the geometric mean?", "type": "numeric", "answer": 1, "tol": 0.001,
 "why": "sqrt(0.5 · 2.0) = sqrt(1) = 1."}
```

```chart
{"title": "Illustration: ratio to seasonal naive on 8 series (synthetic numbers)", "x": "series", "height": 220,
 "series": [
   {"name": "ratio (below 1 is better than seasonal naive)", "kind": "bar", "y": [0.55, 0.7, 0.9, 1.0, 1.1, 0.6, 2.2, 0.8]},
   {"name": "baseline = 1", "gen": [["const", {"value": 1}]], "n": 8, "dash": true}
 ],
 "caption": "One bad series (2.2) hurts the arithmetic mean a lot. The geometric mean is less sensitive to such a single large ratio."}
```

## Public benchmarks (as of this lesson)

- **GIFT-Eval** (Salesforce AI Research, 2024): a benchmark of many data sets across domains, frequencies and horizons, with a public leaderboard. It reports point and probabilistic scores normalized by seasonal naive and aggregated across data sets. It also tracks which models may have seen test data during pre-training.
- **fev-bench** (from the AutoGluon team at Amazon, 2025): a collection of forecasting tasks, including tasks with covariates. Tasks are scored with skill scores and win rates against baselines.
- **TIME** (a newer benchmark): I do not recall its design with confidence. Read its paper and leaderboard page before you quote it.
- Older sets: M3, M4, M5, electricity, traffic, weather. They are small, old, and often part of pre-training corpora.

Leaderboards are **living documents**. A ranking has a date. In an interview or a report, write "as of <date>, on <benchmark version>".

```check
{"q": "A blog says 'Model X is #1 on the leaderboard'. What must you add to make this statement useful?", "type": "single",
 "options": ["The date, the benchmark version and the metric.", "The name of the author's company.", "The colour of the chart."], "answer": 0,
 "why": ["Correct: rankings change and depend on version and metric.", "Not a measure of quality.", "Irrelevant."]}
```

## Leakage and other traps

| Trap | What happens | What to do |
|---|---|---|
| **Pre-training overlap** | The model saw the test series (or a close copy) during pre-training, so zero-shot looks too good | Check the model's data list; prefer benchmarks that mark leaked models; build a private hold-out |
| **Time overlap** | Test period is before the end of pre-training data, even for other series (the world events are shared) | Test on data after the model's data cutoff when possible |
| **Vendor self-reporting** | Vendor picks data sets, metrics, baselines | Re-run on your data; ask for code and settings |
| **Tuning on the benchmark** | After many tries, the model fits the benchmark | Keep a private test set; limit the number of looks |
| **Weak baselines** | "Beats ARIMA" with default settings | Include seasonal naive and tuned simple models |
| **One aggregate number** | Hides where the model fails | Report per-domain and per-horizon scores, and cost |

The Chronos paper is a good example of careful reporting. It separates data sets that were in the training corpus ("in-domain") from data sets not in it ("zero-shot").

```check
{"q": "A model was pre-trained on a public electricity data set. Another paper reports its 'zero-shot' result on the same data set. What is the problem?", "type": "single",
 "options": ["It is not zero-shot: the model saw that data.", "Electricity data cannot be forecast.", "There is no problem."], "answer": 0,
 "why": ["Correct: this is pre-training leakage.", "It can be forecast.", "It inflates the claim."]}
```

## Building a fair harness (your practice problems)

A fair harness has these rules:

1. Same **train/test split** for all models, by time. The model sees only the history.
2. Same **horizon and context** for all models, and the context limit is stated.
3. **Seasonal naive** is always in the table, and ratios are computed against it.
4. **Skip** series where the metric is undefined, such as flat history or history shorter than one season. Do it the same way for all models. Report how many were skipped.
5. Aggregate with the **geometric mean** of ratios, and also show a win rate and the cost (seconds per series).
6. Log **model name, version, date and settings**.

You implement the harness in [[problem:zero-shot-eval-harness]] and the probabilistic score in [[problem:weighted-quantile-loss]].

## Worked example

We compare two models against seasonal naive on 6 series. Watch how the geometric mean and the arithmetic mean of ratios differ, and how win rate adds information.

```python
import numpy as np

# relative MASE (model / seasonal naive) on 6 series, for two models
ratios = {
    "model A (steady)":  np.array([0.9, 0.85, 0.95, 0.9, 0.88, 0.92]),
    "model B (spiky)":   np.array([0.5, 0.4, 0.6, 0.5, 0.45, 2.8]),
}

for name, r in ratios.items():
    arith = r.mean()
    geo = np.exp(np.log(r).mean())
    wins = (r < 1).mean()
    print(f"{name:18s} arithmetic {arith:5.2f}   geometric {geo:5.2f}   win rate {wins:4.0%}")

# the 0.5 / 2.0 example from the text
pair = np.array([0.5, 2.0])
print("pair: arithmetic", pair.mean(), " geometric", float(np.exp(np.log(pair).mean())))

# a skipped-series count is part of an honest report
history_lengths = [5, 40, 30, 3, 100, 60]
season = 12
kept = [n for n in history_lengths if n > season]
print("series kept:", len(kept), "of", len(history_lengths), "(history must be longer than one season)")

# Output:
# model A (steady)   arithmetic  0.90   geometric  0.90   win rate 100%
# model B (spiky)    arithmetic  0.88   geometric  0.65   win rate  83%
# pair: arithmetic 1.25  geometric 1.0
# series kept: 4 of 6 (history must be longer than one season)
```

Model B wins on 5 of 6 series, but one bad series (ratio 2.8) hurts it. Which one is better depends on the cost of a bad series. The table shows both views. Never report only one number.

## Common mistakes

- Comparing against no baseline, or only against a weak one.
- Averaging raw MAE across series with different scales.
- Quoting a leaderboard rank without date, version or metric.
- Treating a zero-shot result as zero-shot when the data set was in the pre-training corpus.
- Silently dropping hard series from one model's table.

## Interview lens

**Typical question:** "A vendor claims their foundation model beats all others. How do you check this?"

**Strong answer:** I ask what data, split, metric and baselines they used. I ask whether the test data could be in the pre-training set. Then I run my own backtest on my series with a time-based split. All models get the same context and horizon. The table includes seasonal naive and a tuned simple model. I use MASE and a quantile metric. I report the ratio to seasonal naive, aggregated with the geometric mean. I add win rate and cost per forecast. I also look at the errors by segment, like short series or intermittent ones. I record the model version and the date.

**Red flags:** accepting a leaderboard rank as proof; averaging raw MAE; no baseline; no mention of leakage.

## Real world

- GIFT-Eval (Salesforce) and fev-bench (Amazon's AutoGluon team) provide public leaderboards on Hugging Face where many foundation models are listed. Check the date and the version shown there.
- The Chronos paper reported results in two groups of data sets (in-domain and zero-shot) to separate fit from generalization.
- The M competitions (M4, M5) set the style of fair evaluation. They use a fixed hold-out, many series, a stated metric, and simple benchmark methods in the table.

## Staff lens

- **Evaluation governance.** Create one internal benchmark. It has golden backtests built from your own series and frozen test periods that no model team may tune on. It also has a champion/challenger rule and a dated results table that anyone can re-run.
- **Offline vs online gap.** An offline win is not a business win. Track forecast value added and the decision metric (stock-outs, cost) after launch.
- **Procurement.** For vendor models, ask for a trial on your data under your harness, with your baselines, before any contract.

## Key points

- Use scale-free metrics (MASE, WQL) and compare to seasonal naive; aggregate ratios with the geometric mean.
- Public leaderboards are living and dated: quote date, version and metric.
- Beware of pre-training leakage, vendor self-reports, and tuning to the benchmark.
- Build your own harness: same split and context, baseline included, undefined series skipped and counted, costs reported.
