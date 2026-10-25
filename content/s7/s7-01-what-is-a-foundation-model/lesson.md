---
id: s7-01-what-is-a-foundation-model
title: What is a time series foundation model?
minutes: 25
level: intermediate
goals: [Explain pre-training, zero-shot forecasting and context length, Describe how a foundation model changes the forecasting workflow, Run a fair zero-shot protocol on unseen series]
prereqs: [s6-07-transformers-for-ts]
tags: [foundation-models, zero-shot, pre-training, 2026-trend]
skills: [baseline-first, scale]
---
## Warm-up

```check
{"q": "In stage 6 you trained a model per data set. What was the training data of a global model?", "type": "single",
 "options": ["Many related series from your own data set", "The whole internet", "Only one series"], "answer": 0,
 "why": ["Correct: a global model learns from many series, but they come from your own data.", "That is the idea of a foundation model, not an ordinary global model.", "A local model uses one series."]}
```

```check
{"q": "Why do we always compare a new model with seasonal naive?", "type": "single",
 "options": ["It is a free baseline that shows if the new model adds value.", "It is the most accurate model.", "It is required by Python."], "answer": 0,
 "why": ["Correct.", "Often it is not.", "No such rule."]}
```

## Why it matters

**2026 trend.** In 2023 the idea of a "GPT for time series" was new. By 2025 and 2026, several pre-trained forecasting models are open source. One line of code gives a forecast for a series the model has never seen. Companies use them for quick first versions, for many small series, and as one member of an ensemble.
Interviewers now ask three things. *What is a foundation model? When does it beat a classical model? How do you test the claim?* This stage gives you the answers.

## The idea in three steps

A [[foundation model]] for time series is a large neural network. It is trained once on a very **large and varied collection of series**. Then it is used on new data.

1. **Pre-training.** Collect many series from many domains (energy, retail, web traffic, weather, finance...). Often some synthetic series are added. Train one model to predict the future from the past.
2. **Zero-shot use.** Give the model the recent history of a new series (the [[context]]) and a horizon. It returns a forecast **without any training on your data**. "Zero-shot" means zero training examples from your data set.
3. **Optional adaptation.** You can fine-tune on your data (lesson 4), or add covariates, or ensemble it with other models.

Compare the workflows:

| Step | Classic / deep model | Foundation model (zero-shot) |
|---|---|---|
| Training on your data | Yes, per series or per data set | No |
| Model selection | Many candidates, tuned per data set | Pick a pre-trained model, check it with a backtest |
| Time to first forecast | Hours or days | Minutes |
| Cost per forecast | Cheap (classical) | Higher (neural network inference) |

```check
{"q": "What does 'zero-shot' mean for a forecasting model?", "type": "single",
 "options": ["It forecasts a new series without any training on your data.", "It forecasts zero values.", "It was trained with zero data."], "answer": 0,
 "why": ["Correct.", "Not related to the values.", "It was pre-trained on a lot of data, but not on yours."]}
```

## Context length and horizon

Every model has two limits:

- **Context length**: how many past values it can read. Some models read 512 values, others up to 16,000 (see lesson 3).
- **Prediction length**: how many future steps one call can produce. Longer horizons use repeated calls or a special head.

If your context is longer than the limit, the model uses only the **most recent** values. If it is shorter, you pass what you have; very short context (a few points) gives weak forecasts.

```chart
{"title": "Context (history the model reads) and horizon (what it predicts)", "x": "step", "height": 220,
 "series": [{"name": "series", "gen": [["trend", {"slope": 0.1, "start": 20}], ["season", {"period": 24, "amp": 4}], ["noise", {"sd": 0.5}]], "n": 168, "seed": 2}],
 "marks": [{"x": 144, "label": "forecast starts (horizon: 24)"}],
 "caption": "The model reads the left part (context) and writes the right part (horizon)."}
```

```check
{"q": "A model has context length 512. Your series has 2,000 past values. What does it read?", "type": "single",
 "options": ["The most recent 512 values", "The first 512 values", "Random 512 values"], "answer": 0,
 "why": ["Correct: the latest history is the most relevant.", "The oldest values are usually less useful.", "Order matters in a series."]}
```

## Why might it work? Why might it not?

**Why it can work.** Many series share simple patterns: daily and weekly cycles, trends, level shifts, noise. A model that has seen millions of such patterns can continue a new series by analogy. This is like a language model continuing a sentence.

**Why it can fail.**

- Your domain has patterns the training data did not have (a special machine, a rare event).
- The series is short or very noisy.
- The pre-training data **already contained your test series** (leakage, lesson 5).
- Strong simple baselines already solve the problem, so there is nothing to gain.

An honest test is therefore always the same. Backtest on your data. Compare with seasonal naive and a tuned classical or boosted-tree model. Compare cost too.

```check
{"q": "A foundation model scores well on a public data set. Why is that not enough to use it on your data?", "type": "single",
 "options": ["Your data may differ from the benchmark, and the benchmark may overlap with its training data.", "Public data sets are always wrong.", "Foundation models cannot read CSV files."], "answer": 0,
 "why": ["Correct.", "They are not always wrong.", "Format is not the issue."]}
```

## Worked example

We write the zero-shot protocol and run it with two simple stand-in models. Real foundation models fit the **same** interface: `forecast(context, horizon)`. The test series are never used for fitting. We score with MASE, which divides the error by the error of a seasonal naive forecast made on the history.

```python
import numpy as np

rng = np.random.default_rng(3)

def make_series(period, n=240):
    t = np.arange(n)
    return 20 + 0.05 * t + 5 * np.sin(2 * np.pi * t / period) + rng.normal(0, 1.0, n)

# five unseen series with different seasonal periods
datasets = [(make_series(p), p) for p in (7, 12, 24, 24, 52)]
H = 12

# a "model" is any function: (context, horizon) -> forecast array
def seasonal_naive(context, horizon, period):
    return np.resize(context[-period:], horizon)

def mean_model(context, horizon, period):
    return np.full(horizon, context[-period:].mean())

def mase(y_true, y_pred, context, period):
    scale = np.abs(context[period:] - context[:-period]).mean()   # in-sample seasonal naive error
    return np.abs(y_true - y_pred).mean() / scale

for name, model in [("seasonal naive", seasonal_naive), ("mean of last season", mean_model)]:
    scores = []
    for series, p in datasets:
        context, future = series[:-H], series[-H:]      # the model sees only the context
        scores.append(mase(future, model(context, H, p), context, p))
    print(f"{name:20s} MASE per series:", np.round(scores, 2), " mean:", round(float(np.mean(scores)), 2))

# Output:
# seasonal naive       MASE per series: [1.18 0.83 1.25 0.99 0.85]  mean: 1.02
# mean of last season  MASE per series: [2.75 2.68 1.86 1.81 0.65]  mean: 1.95
```

A foundation model would be a third entry in this loop: `model(context, H, p)` calls the network. You keep the same split, the same metric and the same baseline.

```notebook
# Run on a machine with PyTorch and the chronos package (check the model card for current usage)
import torch
from chronos import ChronosPipeline

pipeline = ChronosPipeline.from_pretrained("amazon/chronos-t5-small", device_map="cpu", torch_dtype=torch.float32)
context = torch.tensor(series_values)                     # 1D tensor with the history
samples = pipeline.predict(context, prediction_length=12, num_samples=20)   # [1, 20, 12]
median = samples[0].quantile(0.5, dim=0)                  # point forecast
low, high = samples[0].quantile(0.1, dim=0), samples[0].quantile(0.9, dim=0)
```

## Common mistakes

- Skipping the baseline. A foundation model is only worth it if it beats seasonal naive and a tuned simple model on your data.
- Passing an unclean context (wrong frequency, many missing values, outliers) and blaming the model.
- Forgetting the context limit.
- Testing on data from the model's pre-training set.
- Comparing cost per forecast with training cost only; include inference cost at scale.

## Interview lens

**Typical question:** "What is a time series foundation model, and how would you decide to use one?"

**Strong answer:** It is a large model pre-trained on many varied series. It can forecast a new series zero-shot, from the context alone, without training on my data. I would run it on my data with a time-based backtest. I would compare it with seasonal naive, a tuned classical model and a boosted-tree model. I would use a scale-free metric such as MASE, and a probabilistic metric if I need intervals. I would check that my test period is not in its pre-training data, and compare cost and latency. It is attractive for many small series, fast prototypes and cold start. It is less attractive when a simple model is already strong or when cost and explainability matter.

**Red flags:** "it is like ChatGPT so it just works"; no baseline; no talk of leakage or cost.

## Real world

- Amazon released the Chronos models (2024), Google released TimesFM (2024), and Salesforce released Moirai (2024). All three families have open weights and have been updated since. Lessons 2 and 3 give the details.
- Public benchmarks such as GIFT-Eval and fev-bench were built to compare these models across many data sets (lesson 5).

## Staff lens

- **Model selection replaces training.** With foundation models, the work moves from "train per data set" to "select, validate and monitor". Your platform needs a fixed backtest harness and a registry of model versions, because model providers update weights.
- **Version pinning.** Pin model name and weights revision in your config. A silent update can change every forecast.
- **Governance.** Decide who may add a model to the approved list. Require the baseline ladder (seasonal naive, a tuned simple model) as a gate.

## Key points

- A foundation model is pre-trained on many varied series and forecasts new series zero-shot from the context.
- Context length and horizon are hard limits of each model.
- The workflow moves from training to selecting and validating.
- Always test on your data against simple baselines, and check for leakage and cost.
