---
id: s7-02-chronos-family
title: The Chronos family (Chronos, Bolt, Chronos-2)
minutes: 35
level: advanced
goals: [Explain how Chronos turns numbers into tokens (scaling and quantization), Tell Chronos, Chronos-Bolt and Chronos-2 apart, Implement a tokenizer and detokenizer]
prereqs: [s7-01-what-is-a-foundation-model]
tags: [chronos, tokenization, amazon, 2026-trend]
skills: [from-scratch, scale]
---
## Warm-up

```check
{"q": "A series has values 100, 200, 300. After mean scaling (divide by mean of absolute values), what is the scaled value of 300?", "type": "numeric", "answer": 1.5, "tol": 0.001,
 "why": "The mean is 200. 300 / 200 = 1.5."}
```

```check
{"q": "What does a language model predict at each step?", "type": "single",
 "options": ["A probability for each possible next token", "One real number", "A picture"], "answer": 0,
 "why": ["Correct.", "That is a regression model.", "Not related."]}
```

## Why it matters

**2026 trend.** The Chronos models from Amazon are some of the most used open time series foundation models. Their first version has a very clear idea: *treat a time series like a sentence*. If you can explain the tokenizer on a whiteboard, you can explain most of the field. The tokenizer is also a favorite OA task, and you will implement it in the practice problem.

## Chronos (2024): numbers become tokens

Chronos (Ansari et al., Amazon, 2024) re-uses a language model design called **T5** (an encoder-decoder Transformer). A language model reads tokens (integers from a fixed list). So Chronos must turn real numbers into tokens in two steps.

**Step 1: mean scaling.** Divide the context by `scale = mean(|x|)`. Now series of any size (thousands of units or tenths of a degree) have a typical size of about 1.

**Step 2: quantization.** Cut the number line into equal **bins** between a low and a high limit. Each bin has an integer id. A scaled value gets the id of its bin. A few ids are special: PAD (for missing values) and EOS (end of sequence). In the paper's setup the vocabulary has 4,096 tokens.

Small example: 16 bins between −4 and 4 (bin width 0.5). Series `2, 4, 6`.

1. `scale = (2 + 4 + 6) / 3 = 4`. Scaled: `0.5, 1.0, 1.5`.
2. Bin = `floor((v + 4) / 0.5)` = 9, 10, 11. Add 2 for the special tokens: tokens 11, 12, 13.
3. To go back: use the **center** of the bin, times the scale: 3, 5, 7. The error is at most half a bin times the scale.

```widget
{"name": "chronos-tokens", "params": {}}
```

```check
{"q": "Why does Chronos divide by the scale before quantization?", "type": "single",
 "options": ["So series with very different sizes use the same bins.", "To remove the trend.", "To make the series shorter."], "answer": 0,
 "why": ["Correct.", "Scaling does not remove trend.", "The length is unchanged."]}
```

## Training and forecasting

Training is plain language-model training: **predict the next token** with a cross-entropy loss over the bins. The training data are many public series from different domains plus **synthetic** series. The synthetic data in the paper (called KernelSynth) come from random Gaussian processes (smooth random curves combined in different ways).

To forecast, the model samples the next token, appends it, and repeats (autoregressive sampling). It does this many times, giving many sample paths. After detokenizing, the quantiles of the sample paths are the probabilistic forecast, just like DeepAR in stage 6. The Chronos paper released several sizes, from about 20 million to about 700 million parameters.

Trade-offs of the token idea:

| Good | Not so good |
|---|---|
| Probabilistic output is natural: a distribution over bins | Quantization loses precision (bin width) |
| Reuses language model tools | Values outside the range are clipped |
| Works for any scale after scaling | Sampling many long paths is slow |

```check
{"q": "A detokenized value is the center of its bin times the scale. Max error from quantization is:", "type": "single",
 "options": ["Half a bin width times the scale", "One full bin width", "Zero"], "answer": 0,
 "why": ["Correct: the true value is somewhere inside the bin, so at most half a bin from the center (for values inside the range).", "That would be the error if you used an edge.", "Quantization always loses some precision."]}
```

## Chronos-Bolt (late 2024): faster

Chronos-Bolt keeps the T5 family but uses it in a new way, as described by Amazon. It reads the context in **patches** (groups of values). It predicts many future steps **directly** as **quantiles**, instead of sampling one token at a time. This makes it much faster and lighter than the first Chronos, and it was released in several sizes. It is a good default when you need speed.

## Chronos-2 (October 2025): more than one series

Chronos-2 (Amazon, October 2025) is **encoder-only** and aims to handle three cases with one model:

- **Univariate** forecasting: one series.
- **Multivariate** forecasting: several related series forecast together.
- **Covariates**: extra series that help, such as price, promotion or weather (past-only or known in the future).

It uses an attention that works across the items in a group (a *group attention*), so a series can use information from related series and from covariates in the context itself ("in-context learning"). Amazon reported strong results on public benchmarks, including fev-bench and GIFT-Eval. As with any vendor report, check the dates and the current leaderboard (lesson 5).

```check
{"q": "Which Chronos version is designed to use covariates such as price or promotion?", "type": "single",
 "options": ["Chronos (2024)", "Chronos-Bolt", "Chronos-2"], "answer": 2,
 "why": ["The first Chronos is univariate.", "Chronos-Bolt is univariate and focused on speed.", "Correct: it supports univariate, multivariate and covariate tasks."]}
```

## Worked example

We implement the Chronos-style tokenizer and detokenizer (small version) and measure the round-trip error.

```python
import numpy as np

N_BINS, LOW, HIGH = 16, -4.0, 4.0           # small numbers so you can check by hand

def tokenize(x, n_bins=N_BINS, low=LOW, high=HIGH):
    x = np.asarray(x, dtype=float)
    valid = ~np.isnan(x)
    scale = float(np.abs(x[valid]).mean()) if valid.any() else 1.0   # mean scaling
    if scale == 0.0:
        scale = 1.0
    width = (high - low) / n_bins
    b = np.clip(np.floor((np.where(valid, x / scale, 0.0) - low) / width), 0, n_bins - 1).astype(int)
    tokens = b + 2                           # 0 = PAD, 1 = EOS, bins start at 2
    tokens[~valid] = 0                       # missing -> PAD
    return tokens, scale

def detokenize(tokens, scale, n_bins=N_BINS, low=LOW, high=HIGH):
    width = (high - low) / n_bins
    out = (low + (np.asarray(tokens) - 2 + 0.5) * width) * scale     # bin center times scale
    return np.where(np.asarray(tokens) < 2, np.nan, out)

x = np.array([2.0, 4.0, 6.0])
tokens, scale = tokenize(x)
print("tokens:", tokens, "scale:", scale)
print("back  :", detokenize(tokens, scale))

# a series with a missing value and a big outlier
y = np.array([10.0, np.nan, 12.0, 11.0, 90.0])
t2, s2 = tokenize(y)
print("tokens:", t2, "scale:", round(s2, 2))
print("back  :", detokenize(t2, s2).round(1))

# more bins give a smaller error
rng = np.random.default_rng(0)
z = rng.normal(100, 15, 500)
for nb in (16, 64, 256):
    tk, sc = tokenize(z, n_bins=nb)
    err = np.abs(detokenize(tk, sc, n_bins=nb) - z).mean()
    print(f"{nb:4d} bins: mean abs error {err:.2f}")

# Output:
# tokens: [11 12 13] scale: 4.0
# back  : [3. 5. 7.]
# tokens: [10  0 10 10 15] scale: 30.75
# back  : [ 7.7  nan  7.7  7.7 84.6]
#   16 bins: mean abs error 14.09
#   64 bins: mean abs error 2.96
#  256 bins: mean abs error 0.81
```

Look at the outlier: 90 is much larger than the rest, so the scale becomes large (30.75). The small values then fall in only a few bins, and precision drops. Outliers hurt mean scaling, so clean them or clip them first.

```notebook
# Chronos-Bolt with the chronos package (check the model card for the current API)
import torch
from chronos import BaseChronosPipeline

pipeline = BaseChronosPipeline.from_pretrained("amazon/chronos-bolt-small", device_map="cpu", torch_dtype=torch.float32)
quantiles, mean = pipeline.predict_quantiles(
    context=torch.tensor(series_values), prediction_length=24, quantile_levels=[0.1, 0.5, 0.9]
)
# quantiles has shape [1, 24, 3]
```

## Common mistakes

- Putting very long histories with outliers into mean scaling (one huge value makes all others small).
- Treating the token ids as numbers (token 13 is not "bigger" in a simple linear way after scaling).
- Using the wrong range, so values are clipped.
- Forgetting that the frequency and calendar are not an input in the first Chronos: the model sees only values.
- Assuming Chronos-2 covariate support means it understands causes. It uses patterns in the context.

## Interview lens

**Typical question:** "How does Chronos turn a time series into something a language model can read?"

**Strong answer:** It scales each context by the mean of the absolute values so different series have a similar size. Then it quantizes the scaled values into a fixed number of equal bins, and each bin is a token; a few extra tokens mark padding and the end. A T5 language model is trained to predict the next token, and at forecast time it samples many paths, and I read quantiles from them after mapping tokens back to bin centers. The trade-offs are precision loss from the bin width, clipping outside the range, and the cost of sampling. Chronos-Bolt predicts quantiles directly for speed, and Chronos-2 adds multivariate and covariate support.

**Red flags:** thinks Chronos regresses a number directly; forgets scaling; cannot say why outliers hurt.

## Real world

- Chronos was published by Amazon researchers (Ansari et al., 2024) with open weights on Hugging Face and is also available through Amazon's tools such as AutoGluon-TimeSeries.
- Chronos-Bolt (November 2024) and Chronos-2 (October 2025) extended the family. Check the official model cards for sizes and licenses before use.

## Staff lens

- **Evaluation governance.** Vendor and paper results use specific benchmarks and dates. Re-run them in your harness before any decision.
- **Build vs buy.** Chronos is open: you can host it yourself. Compare the cost of GPU hosting with a hosted API, and compare with a fast classical ensemble that costs almost nothing per series.
- **Risk.** Pin the version, and keep a fallback (seasonal naive) when the model service fails.

## Key points

- Chronos: mean scaling, then uniform quantization into bins (tokens), then a T5 language model trained on next-token prediction.
- Sample many paths and detokenize to get quantiles. The error from binning is at most half a bin times the scale.
- Chronos-Bolt: patches in, quantiles out, faster. Chronos-2 (Oct 2025): encoder-only, univariate, multivariate and covariates.
- Outliers and clipping are weak points of mean scaling.
