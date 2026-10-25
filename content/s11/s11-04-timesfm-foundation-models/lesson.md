---
id: s11-04-timesfm-foundation-models
title: Google TimesFM and the foundation-model wave
minutes: 25
level: advanced
goals: [Explain how TimesFM uses patches and a decoder-only transformer, List other time-series foundation models, Judge claims about foundation models with a fair test]
prereqs: [s11-03-deepar-gluonts-chronos]
tags: [timesfm, foundation-model, patches, transformer, zero-shot]
skills: [case-studies, deep-learning-ts]
---

## Warm-up

```check
{"q": "How does Chronos turn a value into a token?", "type": "single",
 "options": ["It scales the series and puts the value in a bin", "It writes digits as text", "It clusters values with k-means"],
 "answer": 0,
 "why": ["Correct.", "Chronos uses bins, not digit text.", "No clustering is used."]}
```

```check
{"q": "What does zero-shot forecasting mean?", "type": "single",
 "options": ["No training on the new series", "No features", "No error"],
 "answer": 0,
 "why": ["Correct.", "Features may be used.", "Errors still exist."]}
```

## Why it matters

Large language models learned to write text by reading huge amounts of text. Researchers asked: can we do the same for time series? One model, trained once on a huge and varied collection of series, then used on new data with no training. Google Research built **[[TimesFM]]** (Time Series Foundation Model) to test this idea. Whether it works in your business is an open question. So you must know both the idea and how to test it.

## TimesFM in one page

TimesFM (Das, Kong, Sen and Zhou, Google Research; ICML 2024) has these ideas:

- **Decoder-only transformer.** Like GPT: it reads a sequence and predicts what comes next.
- **Patches, not points.** It groups consecutive values into a **[[patch]]**, for example 32 values. It treats each patch as one "word". A small network turns a patch into a vector. The model then predicts the **next patch**, which can be longer than the input patch. Longer output patches make forecasting long horizons faster, with fewer steps.
- **Pretraining on a large mix of data.** The paper describes real data, such as Google Trends and Wikipedia page views. It also uses synthetic series. The model has about 200 million parameters, small compared with language models.
## Using TimesFM

Two more ideas describe how you use the model.

- **Zero-shot use.** You give it the history of any series, and it forecasts. No fitting. The paper reports zero-shot accuracy close to supervised models on public benchmarks.
- **Point forecasts first.** The original model gives a point forecast. Later releases added quantile outputs. Check the current documentation for details.

```widget
{"name": "sliding-window", "params": {}}
```

The widget shows a window moving over a series. With patches, the window moves by a whole patch.

```check
{"q": "Why use patches instead of single points as the model's input units?", "type": "single",
 "options": ["Patches remove noise completely", "Fewer tokens means a much cheaper attention computation and a longer context", "Patches are required by Python", "Patches allow covariates"],
 "answer": 1,
 "why": ["They reduce length, not noise.", "Correct: attention cost grows with the square of the number of tokens.", "Not a Python rule.", "Covariates are a separate matter."]}
```

## The wider family

| Model | Group | Idea |
|---|---|---|
| **Chronos** (and Chronos-Bolt) | Amazon | Quantise values into tokens, T5 model |
| **TimesFM** | Google | Patches, decoder-only transformer |
| **Moirai** | Salesforce | Masked encoder, handles many frequencies and extra variables |
| **Lag-Llama** | Academic group | Decoder-only model using lag features, probabilistic output |
| **TimeGPT** | Nixtla | Commercial model, used through an API |

New models appear every few months, so do not memorise versions. Learn the common design: pretrain on many series, scale inputs, output a forecast or a distribution, use zero-shot or fine-tune.

```check
{"q": "Which is true for most time-series foundation models?", "type": "single",
 "options": ["They are pretrained on many series and can be used without training on yours", "They replace the need for any data", "They always give exact forecasts", "They only work for daily data"],
 "answer": 0,
 "why": ["Correct.", "You still need history for the series you forecast.", "No model gives exact forecasts.", "Most handle several frequencies."]}
```

## How to judge a claim

Papers and blogs say a foundation model "beats" others. Before you believe it in your own work, ask:

1. **Which baselines?** Seasonal naive, ETS, and a tuned global GBM must be in the table.
2. **Which metric?** MASE or WAPE, and a quantile metric if intervals matter.
3. **Which split?** A rolling origin, and a time **after** the model's pretraining data. A model may have seen your public dataset (or a version of it) during pretraining. This is **test leakage** at the benchmark level.
4. **Cost?** Latency, GPU hours, and money per million series.
5. **Covariates?** Does it use price, promotions, weather? Many cannot.

Practical use: run it as a **zero-shot baseline** and as a feature or ensemble member. Fine-tuning may help on your domain.

```check
{"q": "A blog shows a foundation model beating ARIMA on a public dataset. What is the first question you ask?", "type": "single",
 "options": ["How many GPUs did they use?", "Was the dataset possibly in the pretraining data, and were strong baselines (seasonal naive, ETS, GBM) included?", "Which color are the charts?", "Who wrote the blog?"],
 "answer": 1,
 "why": ["Cost matters, but validity comes first.", "Correct: leakage and weak baselines are the most common problems.", "Irrelevant.", "Authority does not replace evidence."]}
```

## Worked example

We show patching and why it matters for cost. A context of 512 values becomes 16 patches of 32. Attention cost grows with the square of the number of tokens.

```python
import numpy as np

rng = np.random.default_rng(0)
t = np.arange(512)
series = 100 + 10 * np.sin(2 * np.pi * t / 32) + rng.normal(0, 1, 512)

patch_len = 32
patches = series.reshape(-1, patch_len)             # shape (16, 32): 16 tokens of 32 values each
print("patches:", patches.shape)

cost_points = len(series) ** 2                      # attention pairs if every point is a token
cost_patches = len(patches) ** 2                    # attention pairs with patches
print("attention pairs, points :", cost_points)
print("attention pairs, patches:", cost_patches, "->", cost_points // cost_patches, "times cheaper")

# A trivial 'next patch' forecaster: repeat the last patch (this equals seasonal naive with period 32)
context, truth = patches[:-1], patches[-1]
forecast = context[-1]
print("MAE of repeating the last patch:", round(float(np.mean(np.abs(truth - forecast))), 2))
# Output:
# patches: (16, 32)
# attention pairs, points : 262144
# attention pairs, patches: 256 -> 1024 times cheaper
# MAE of repeating the last patch: 1.08
```

The model predicts a whole patch at once. A transformer would replace the last two lines with a learned model, but the data shape is the same.

## Common mistakes

- Believing a foundation model needs no baseline.
- Comparing on a dataset that may be part of its pretraining data.
- Ignoring cost: a large model on millions of series needs many GPUs.
- Forgetting that many models are target-only (no price or promotion information).
- Using it for a series with very short history or unusual behaviour without checks.

## Interview lens

**Typical question:** "Would you use a time-series foundation model in production?"

**Strong answer:** I would test it first as a zero-shot baseline. I compare it with seasonal naive, ETS and a tuned global GBM. I use a rolling-origin backtest and a metric that fits the decision. I would check for leakage from pretraining data, look at cost and latency, and see if I need covariates. If it wins by a margin that pays for its cost, I use it. I might use it in an ensemble or with fine-tuning. If not, a simple model is easier to run and explain.

**Red flags:** "It is the best model, I use it for everything." Not asking about pretraining data. No cost estimate.

## Real world

Google Research announced TimesFM in 2023 and presented it at ICML 2024. A version of the model is available publicly. Other groups released their own models in 2023-2024. At the same time, benchmark papers have asked how much foundation models beat strong, tuned baselines. The honest answer is: they are very good baselines, and the picture changes with each release.

## Key points

- TimesFM: decoder-only transformer on patches, pretrained on a large mix of real and synthetic series, used zero-shot.
- Patches reduce the token count, so attention is cheaper and the context can be longer.
- Other models: Chronos, Moirai, Lag-Llama, TimeGPT. Versions change fast.
- Judge claims by baselines, split, metric, leakage from pretraining data, cost and covariates.
- Use them as strong zero-shot baselines and ensemble members.
