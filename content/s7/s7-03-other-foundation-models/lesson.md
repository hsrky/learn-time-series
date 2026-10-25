---
id: s7-03-other-foundation-models
title: TimesFM, Moirai and the model zoo
minutes: 30
level: advanced
goals: [Describe TimesFM 2.5 and Moirai 2.0 in simple words, Place TTM, Lag-Llama, MOMENT, TimeGPT, Toto and others on a map, Read a model card for size, context and license]
prereqs: [s7-02-chronos-family]
tags: [timesfm, moirai, model-zoo, 2026-trend]
skills: [scale, communication]
---
## Warm-up

```check
{"q": "Which Chronos version is encoder-only and supports covariates?", "type": "single",
 "options": ["Chronos-Bolt", "Chronos-2", "Chronos (2024)"], "answer": 1,
 "why": ["Chronos-Bolt focuses on speed.", "Correct.", "The first Chronos uses an encoder-decoder T5 and is univariate."]}
```

```check
{"q": "In PatchTST, what is a token?", "type": "single",
 "options": ["A patch of consecutive values", "One word", "One variable's whole history"], "answer": 0,
 "why": ["Correct. TimesFM also reads the input in patches.", "There is no text.", "That is iTransformer."]}
```

## Why it matters

**2026 trend.** There is no single "the" foundation model. New models appear every few months, and a team must keep a mental map: who made it, how it works, how big it is, and what its license allows. Interviewers like candidates who can describe two or three models well and say honestly what they do **not** know about the rest.

Rule for this lesson and for your interview: say only what you are sure of. "I believe it is decoder-only, I would check the model card" is a good answer.

## TimesFM (Google Research)

- **Paper:** Das, Kong, Sen and Zhou, ICML 2024. The model is **decoder-only**: like GPT, it reads patches of values and predicts the next patch, from left to right.
- It reads the context in **patches**, and it can output a longer patch than it reads. That lets it forecast a long horizon in few steps.
- Pre-training data: a large mix of real series (for example web search interest and Wikipedia page views) and synthetic series.
- **TimesFM 2.5 (September 2025):** about 200 million parameters (smaller than the 2.0 release), and a context length of up to 16,000 values. It is open source.

Why the long context matters: with 16,000 hourly values you can show the model almost two years of history, which is more than one full yearly season. With 512 values you show about three weeks.

```check
{"q": "A context of 16,000 hourly points covers about how many days?", "type": "numeric", "answer": 667, "tol": 1,
 "why": "16,000 / 24 = 666.7 days."}
```

## Moirai (Salesforce AI Research)

- **Moirai (2024)** by Woo et al. was designed for **any-variate** forecasting: one model for series with a different number of variables. It uses a special attention that handles variables flagged by an id, patches of several sizes, and a flexible output distribution. Its training collection is called LOTSA, a large open archive of time series from many domains.
- **Moirai 2.0:** Salesforce changed the design to **decoder-only**. Read the release notes for sizes and reported benchmark results, and check the date of each claim.

## The wider model zoo

I list what I am confident about. For anything else, read the model card.

| Model | Who | What to remember |
|---|---|---|
| **TTM** (TinyTimeMixers) | IBM Research | Very small models (starting around one million parameters) built from simple mixing layers (no attention). Cheap to run and to fine-tune, even on a CPU. |
| **FlowState** | IBM Research | A newer IBM time series model. I do not recall design details; check the model card before you say more. |
| **Lag-Llama** | Rasul et al., 2023 | One of the first open decoder-only models. It uses lagged values as inputs and outputs a distribution (probabilistic). |
| **MOMENT** | CMU (Auton Lab) | A family for many tasks: forecasting, classification, anomaly detection, imputation. Trained by masking and reconstructing. |
| **TimeGPT** | Nixtla | Closed model used through an **API**. Supports fine-tuning and extra variables via the service. You do not host it. |
| **Toto** | Datadog | A decoder-only model focused on **observability** data (infrastructure and application metrics). Released openly with a benchmark of observability metrics. |
| **Timestral** | Mistral AI | I do not have reliable details. Treat it as "check the official announcement and model card". |

A few simple ideas to compare any model quickly: *open weights or API? Univariate or multivariate? Covariates? Probabilistic output? Context length? Size? License?*

```check
{"q": "Your data are server CPU and memory metrics from a large cloud system. Which model from the table was designed for this kind of data?", "type": "single",
 "options": ["Toto", "Lag-Llama", "MOMENT"], "answer": 0,
 "why": ["Correct: Toto targets observability metrics (check the model card for details).", "Lag-Llama is a general-purpose probabilistic model.", "MOMENT is a general multi-task family."]}
```

```chart
{"title": "Model sizes used in the worked example (millions of parameters)", "x": "model", "height": 200,
 "series": [{"name": "parameters (M)", "kind": "bar", "y": [1, 20, 200, 710]}],
 "caption": "From left: a tiny TTM-like model (1M), Chronos-T5 mini (20M), TimesFM 2.5 (about 200M), Chronos-T5 large (710M)."}
```

## How to choose, in practice

1. **Constraints first:** can data leave your network? (API models need that.) What latency and cost can you pay per forecast?
2. **Data fit:** do you need covariates, multivariate input, long context, or intervals?
3. **Benchmark on your data:** two or three candidates plus seasonal naive and a tuned simple model. Do not trust a ranking from one leaderboard.
4. **Look at the license** (some model licenses limit commercial use).
5. **Plan for change:** a better model will probably appear in six months. Keep your pipeline model-agnostic.

```check
{"q": "Customer data must not leave your company network. Which option is ruled out first?", "type": "single",
 "options": ["A model used only through a vendor API", "A model with open weights hosted by you", "Seasonal naive"], "answer": 0,
 "why": ["Correct: the API needs your data to be sent out.", "You host it yourself, so data stay inside.", "It runs anywhere."]}
```

## Worked example

We compute memory and context numbers. Reading a model card is a skill: size in parameters tells you the memory to load the model.

```python
# memory to hold the weights: parameters x bytes per number
# float32 = 4 bytes, bfloat16/float16 = 2 bytes
def weights_mb(params_millions, bytes_per_param):
    return params_millions * 1e6 * bytes_per_param / 1e6   # megabytes

models = {"TTM-like tiny (1M)": 1, "Chronos-T5 mini (20M)": 20,
          "TimesFM 2.5 (200M)": 200, "Chronos-T5 large (710M)": 710}
for name, m in models.items():
    print(f"{name:28s} fp32 {weights_mb(m, 4):7.0f} MB   bf16 {weights_mb(m, 2):7.0f} MB")

# context length in days for hourly data
for ctx in (512, 2048, 16000):
    print(f"context {ctx:6d} hourly values = {ctx / 24:6.1f} days")

# how many patches of 32 values fit in a 16,000 value context?
print("patches of 32 in 16,000 values:", 16000 // 32)

# Output:
# TTM-like tiny (1M)           fp32       4 MB   bf16       2 MB
# Chronos-T5 mini (20M)        fp32      80 MB   bf16      40 MB
# TimesFM 2.5 (200M)           fp32     800 MB   bf16     400 MB
# Chronos-T5 large (710M)      fp32    2840 MB   bf16    1420 MB
# context    512 hourly values =   21.3 days
# context   2048 hourly values =   85.3 days
# context  16000 hourly values =  666.7 days
# patches of 32 in 16,000 values: 500
```

Weights are only part of the memory; you also need memory for the data and the activations. But this quick estimate tells you at once that a 200M model fits on a laptop, and a 1M model fits almost anywhere.

## Common mistakes

- Repeating a model's claims from memory, with wrong sizes or dates. Say "according to the model card" and check.
- Choosing by leaderboard rank only (lesson 5).
- Forgetting the license or the data policy for API models.
- Comparing models with different context lengths and calling it fair.
- Using the biggest model by default. A small model often does the job at a fraction of the cost.

## Interview lens

**Typical question:** "Name some time series foundation models and how they differ."

**Strong answer:** Chronos from Amazon turns scaled values into tokens for a T5 model; Chronos-2 adds multivariate and covariate support. TimesFM from Google is decoder-only and works on patches, and version 2.5 has about 200 million parameters and a context of up to 16,000 values. Moirai from Salesforce was built for any number of variables and its 2.0 version is decoder-only. IBM's TinyTimeMixers are very small and cheap to fine-tune, TimeGPT is an API product, Toto from Datadog targets observability data, and MOMENT covers many tasks. I would compare them on my data with seasonal naive, check license and data policy, and re-check the list often, because it changes quickly.

**Red flags:** naming only one model; inventing parameter counts; saying that foundation models "replace" all other methods.

## Real world

- Open weights of Chronos, TimesFM, Moirai, TTM, Lag-Llama, MOMENT and Toto are published on Hugging Face by their authors. TimeGPT is available only through Nixtla's API.
- Teams commonly test two or three of these against their own baselines and keep the best per use case. Some combine them in an ensemble (lesson 4).

## Staff lens

- **Build vs buy.** Hosting open weights costs GPU or CPU time and engineering effort. An API costs per call and sends data out. A classical ensemble costs almost nothing per forecast. Do the cost per 1,000 forecasts for each option at your real volume.
- **Vendor risk.** An API model can change, get more expensive or be discontinued. Keep a fallback and a model-agnostic interface.
- **Evaluation governance.** Keep a dated table of "model, version, weights revision, benchmark date, license" in your registry. Review it every quarter.

## Key points

- TimesFM 2.5: decoder-only, patches, about 200M parameters, context up to 16k. Moirai 2.0: decoder-only successor of the any-variate Moirai.
- The zoo: TTM (tiny), Lag-Llama, MOMENT (multi-task), TimeGPT (API), Toto (observability), and more.
- Choose by constraints (data policy, latency, cost), data fit, and your own backtest.
- Only state facts you are sure of. Check model cards, dates and licenses.
