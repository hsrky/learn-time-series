---
id: s7-04-zero-shot-finetune-routers
title: Zero-shot, fine-tuning, ensembles and routers
minutes: 30
level: advanced
goals: [Choose between zero-shot, fine-tuning and training from scratch, Explain why forecast ensembles work, Explain a model router and its overfitting risk]
prereqs: [s7-03-other-foundation-models]
tags: [fine-tuning, ensemble, router, model-selection, 2026-trend]
skills: [backtest, baseline-first, scale]
---
## Warm-up

```check
{"q": "Which setting means 'no training on your data'?", "type": "single",
 "options": ["Zero-shot", "Fine-tuning", "Training from scratch"], "answer": 0,
 "why": ["Correct.", "Fine-tuning trains on your data.", "Scratch training also uses your data."]}
```

```check
{"q": "Why must the validation period come after the training period in time?", "type": "single",
 "options": ["To avoid leaking future information into training.", "Because it looks nicer.", "To make the model larger."], "answer": 0,
 "why": ["Correct.", "Not a reason.", "Not related."]}
```

## Why it matters

After you pick a foundation model, you still face three design questions:

1. Use it **as it is** (zero-shot), **adapt** it (fine-tune), or train your own?
2. Use **one** model, or **combine** several?
3. If you have several models, choose per series with a **router**, or use the same one for all?

**2026 trend:** strong results on public leaderboards often come from *ensembles* that mix foundation models with classical and boosted-tree models. This lesson explains why, and where it goes wrong.

## Zero-shot, fine-tuning, from scratch

| Option | Training data used | Cost | When it fits |
|---|---|---|---|
| **Zero-shot** | none from you | lowest | quick start, many short series, cold start |
| **In-context help** | related series or covariates passed in the context | low | models that accept covariates or groups (for example Chronos-2) |
| **Fine-tuning** | your series | medium | enough data, your domain is unusual, zero-shot is clearly beaten by a tuned model |
| **From scratch** | your series | highest | very large private data, special needs, you want full control |

**Fine-tuning** continues the training of the pre-trained model on your data, usually with a small learning rate. *Full* fine-tuning changes all weights. *Parameter-efficient* fine-tuning (for example [[LoRA]]) trains only a few small extra matrices and keeps the rest frozen. It is cheaper and lowers the risk of overfitting.

Risks of fine-tuning:

- **Overfitting** to a small data set. Use a time-based validation set and early stopping.
- **Forgetting** the general skill, so it gets worse on new patterns.
- **Leakage:** the fine-tuning windows must end before the evaluation period starts.
- Extra cost: a training pipeline, GPU time, and a new model to monitor.

```check
{"q": "You fine-tune on the last 2 years and evaluate on the same last 2 years. What is wrong?", "type": "single",
 "options": ["The evaluation data were used for training, so the score is too good.", "Nothing, it is standard.", "The model is too small."], "answer": 0,
 "why": ["Correct: this is leakage. Hold out a later period.", "It is not standard.", "Size is not the issue."]}
```

## Ensembles: why averaging helps

An [[ensemble]] combines the forecasts of several models, for example by averaging or taking the median. It works when the models make **different errors**.

Numbers: two models forecast demand of 100.
- Model A says 90 (error −10). Model B says 112 (error +12).
- The average is 101. The error is only +1.

If the errors are independent with the same size, averaging `k` models cuts the error spread by `√k`. In real life errors are correlated, so the gain is smaller but usually still positive. Mix **different kinds** of models (a foundation model, an exponential smoothing model, a boosted-tree model) for the best gain.

A *weighted* ensemble gives more weight to the models with better validation scores. AutoGluon-TimeSeries (Amazon) is an example of a library that builds weighted ensembles of statistical, deep and Chronos models.

```chart
{"title": "Two models with opposite errors, and their average", "x": "step", "height": 220,
 "series": [
   {"name": "truth", "gen": [["const", {"value": 100}], ["season", {"period": 12, "amp": 8}]], "n": 36},
   {"name": "model A (too low)", "gen": [["const", {"value": 92}], ["season", {"period": 12, "amp": 8}]], "n": 36, "dash": true},
   {"name": "model B (too high)", "gen": [["const", {"value": 108}], ["season", {"period": 12, "amp": 8}]], "n": 36, "dash": true},
   {"name": "average", "gen": [["const", {"value": 100}], ["season", {"period": 12, "amp": 8}]], "n": 36}
 ],
 "caption": "The errors cancel in the average. This is a simplified picture: real errors are never exactly opposite."}
```

```check
{"q": "Three independent models each have error spread 6. About what spread does their average have?", "type": "numeric", "answer": 3.46, "tol": 0.05,
 "why": "6 / √3 = 3.46."}
```

## Routers: pick a model per series

A [[router]] chooses, for each series (or group of series), which model to use. It uses validation errors or series features (length, seasonality strength, intermittency).

Idea: different series prefer different models. A smooth seasonal series suits one model; a short noisy series suits another.

The danger is **selection noise**. With many models and short validation windows, the model that wins on validation is often just lucky. On the next period, the router's choice is not better than one global model, and can be worse. This is the "winner's curse".

Protect yourself:

- Use a **long** validation window and several forecast origins.
- Prefer routing by **groups** (for example by frequency or length) instead of per series.
- Keep the router **simple**, or average the top two or three models.
- Measure the router on a **later test period** that was not used to build it (that is what the practice problem does).

```check
{"q": "A router picks the best of 8 models for each series using one 7-day validation window. On the next period it is no better than the best single model. Most likely reason?", "type": "single",
 "options": ["The validation winner was often just lucky (selection noise).", "Routers cannot work.", "The test period was too short."], "answer": 0,
 "why": ["Correct.", "They can help when differences between models are real and the validation is long enough.", "A short test period adds noise but is not the main cause here."]}
```

## Worked example

We simulate 3 models on 200 series. The truth is 0 everywhere, so the forecast itself is the error. Each model has fresh noise in every window. In case B, each model also has a **persistent bias per series** (a series it handles badly). We compare the best single model, a router and the average of the three forecasts on a later test window.

```python
import numpy as np

rng = np.random.default_rng(0)
S, H, M = 200, 12, 3                      # series, horizon, models

def run(sd_bias):
    bias = rng.normal(0, sd_bias, size=(M, S, 1))      # persistent per-series bias of each model
    def window():                                       # truth = 0, so forecast = error
        return bias + rng.normal(0, 1.0, size=(M, S, H))
    fv, ft = window(), window()                         # validation window, then a later test window
    val = np.abs(fv).mean(axis=2)                       # [M, S] validation errors
    tst = np.abs(ft).mean(axis=2)                       # [M, S] test errors
    choice = val.argmin(axis=0)                         # router: best model per series on validation
    glob = val.mean(axis=1).argmin()                    # one single best model for all series
    router = tst[choice, np.arange(S)].mean()
    single = tst[glob].mean()
    ensemble = np.abs(ft.mean(axis=0)).mean()           # average the three forecasts, then score
    return round(float(single), 3), round(float(router), 3), round(float(ensemble), 3)

print("A: models equal         (single, router, ensemble):", run(0.0))
print("B: real differences     (single, router, ensemble):", run(1.5))

# Output:
# A: models equal         (single, router, ensemble): (0.787, 0.801, 0.457)
# B: real differences     (single, router, ensemble): (1.392, 0.969, 0.84)
```

Case A: the models are equal, so the router has no real edge. It is not better than the single model; its small loss comes from selection noise. Case B: the differences are real and large, so the router wins clearly against the single model, and the ensemble is better still. The ensemble is very good in this simulation because the errors of the three models are fully independent. Real models make correlated errors, so the real gain is smaller. Always measure it on your data.

## Common mistakes

- Fine-tuning and testing on overlapping periods.
- Building the router on the same window used to report its score.
- Ensembling nearly identical models (no diversity, no gain).
- Using an average of quantiles from different models and calling it a calibrated interval without checking coverage.
- Forgetting that every extra model adds cost, latency and a failure mode.

## Interview lens

**Typical question:** "You have Chronos-Bolt, a LightGBM model and ETS. How do you combine them?"

**Strong answer:** First I run all three, plus seasonal naive, on the same time-based backtest with several origins and compare them with a scale-free metric and a probabilistic metric. Then I try a simple average or median, and a weighted average with weights fitted on an earlier window and tested on a later one. A per-series router is the last thing I try, because selection noise often cancels its gain; if I use one, I route by groups and measure it on a held-out later period. I also compare total cost and latency, because three models cost three times as much to serve.

**Red flags:** choosing the best model per series on the same data used for reporting; ignoring cost; claiming ensembles always win.

## Real world

- The M4 and M5 forecasting competitions showed that combinations of different methods were among the strongest approaches (the M4 winner combined exponential smoothing and neural networks; many top M5 entries combined several LightGBM models).
- AutoGluon-TimeSeries (from Amazon) builds ensembles that can include Chronos models next to statistical and deep learning models.
- Public leaderboards for foundation models often list ensembles. Check how the ensemble was built and which data it used.

## Staff lens

- **Build vs buy.** An ensemble of three models costs about three times as much to run. The platform decision is whether the accuracy gain (in money) beats the extra cost and complexity, per segment of series. Many teams use a cheap ensemble for the long tail and a heavy one for the 5% of series that drive the revenue.
- **Evaluation governance.** Router and ensemble weights are trained on data. They need their own held-out test period and a rule: no change goes live without a champion/challenger test on a later period.
- **Reliability.** Define fallbacks: if the foundation model service fails, serve the last good forecast or seasonal naive, and alert.

## Key points

- Zero-shot is cheapest; fine-tune only when data are enough and zero-shot is clearly beaten; always keep fine-tune and test periods apart.
- Ensembles help when models make different errors; mix different kinds of models.
- Routers suffer from selection noise: use long validation windows, group-level routing and a later test period.
- Count cost and latency in every decision.
