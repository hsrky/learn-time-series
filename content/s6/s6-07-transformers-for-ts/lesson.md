---
id: s6-07-transformers-for-ts
title: Transformers for time series
minutes: 35
level: advanced
goals: [Explain self-attention and why plain attention is costly for long series, Describe the path Informer, Autoformer, PatchTST and iTransformer, Implement patching and count tokens]
prereqs: [s6-03-tcn-causal-convolutions, s6-06-temporal-fusion-transformer]
tags: [transformer, attention, patchtst, itransformer, informer, autoformer]
skills: [from-scratch, scale]
---
## Warm-up

```check
{"q": "Series length 512, kernel 2. About how many layers does a dilated TCN (dilations 1, 2, 4, ...) need to see all 512 steps?", "type": "numeric", "answer": 9, "tol": 0,
 "why": "Dilations 1 to 256 are 9 layers. RF = 1 + (1+2+...+256) = 512."}
```

```check
{"q": "In TFT, what does the attention layer let a future step do?", "type": "single",
 "options": ["Look at any past step and weigh it.", "Only look at the previous step.", "Skip the input."], "answer": 0,
 "why": ["Correct.", "That is the idea of an RNN.", "Not the purpose."]}
```

## Why it matters

Transformers changed language models. Between 2020 and 2024, many researchers tried them for forecasting. The story has twists. First came complex models. Then a simple linear baseline beat them (next lesson). Then two designs, PatchTST and iTransformer, made Transformers competitive again.
**Good to know:** several later models reuse the patching idea from PatchTST. You will meet some of them in stage 7.

## Self-attention and its cost

[[Self-attention]] lets every position in a sequence look at all other positions. For each token it makes three vectors: a **query** Q, a **key** K and a **value** V.

`Attention(Q, K, V) = softmax( Q·Kᵀ / √d ) · V`

- `Q·Kᵀ`: a table of scores. Entry (i, j) says how much token i should look at token j.
- `√d`: keeps the scores in a stable range (`d` = size of the key vector).
- `softmax`: turns each row into weights that sum to 1.
- The result is a weighted average of the value vectors.

The score table has `n × n` entries for `n` tokens. Time and memory grow with **n squared**. If every time step is a token, a window of 512 steps needs 262,144 scores per head per layer. A window of 5,000 steps would need 25 million.

```check
{"q": "You double the number of tokens. By what factor does the attention score table grow?", "type": "numeric", "answer": 4, "tol": 0,
 "why": "n² becomes (2n)² = 4n²."}
```

## Informer and Autoformer: make attention cheaper

- **Informer** (Zhou et al., AAAI 2021, best paper award): *ProbSparse attention* lets only the most useful queries do full attention. Cost falls to about `n log n`. It also predicts the whole horizon in one pass (not step by step).
- **Autoformer** (Wu et al., NeurIPS 2021): builds **series decomposition** inside the network. This is trend + remainder, as in classical methods. It replaces attention by an *auto-correlation* layer that finds repeating lags in the series.
- **FEDformer** (2022) works in the frequency domain.

These papers showed good results on long-term forecasting benchmarks (electricity, traffic, weather, the ETT transformer-temperature data). The next lesson explains why those results were later questioned.

## PatchTST: patches and channel independence

PatchTST makes two simple changes. It comes from Nie, Nguyen, Sinthong and Kalagnanam (ICLR 2023, paper title "A Time Series is Worth 64 Words").

**1. Patching.** Cut each series into short overlapping **patches** (for example length 16, stride 8). Each patch becomes one token. A window of 512 steps becomes 64 tokens. The attention table shrinks from 512² to 64²: 64 times smaller. It also gives each token a local shape, like a word.

**2. Channel independence.** If you have 7 variables (channels), process each as its own univariate series, with the **same shared weights**. Channels are not mixed in the model. This sounds odd, but it reduced overfitting in the paper's benchmarks and is simple to train.

Also: the paper adds *RevIN* normalization (two lessons later) and a self-supervised pre-training option (mask some patches and reconstruct them).

```chart
{"title": "Tokens needed for 512 steps", "x": "method", "height": 200,
 "series": [{"name": "tokens", "kind": "bar", "y": [512, 64]}],
 "caption": "Point tokens (left): 512. Patch tokens with length 16 and stride 8 (right): 64. Attention cost is about the square of this number."}
```

```check
{"q": "512 steps, patch length 16, stride 8, with end padding of 8. How many patches?", "type": "numeric", "answer": 64, "tol": 0,
 "why": "Padded length 520. (520 − 16) // 8 + 1 = 63 + 1 = 64."}
```

## iTransformer: variates as tokens

**iTransformer** (Liu et al., ICLR 2024) turns the tokens around ("inverted"). Instead of one token per time step, it makes **one token per variable (variate)**. The whole history of one variable is embedded into one vector.

- **Attention** now works **between variables**: it learns which variables relate to which (for example, electricity use in two connected areas).
- The **feed-forward network** works on each variable's series and learns its time patterns.

Compare the two:

| | PatchTST | iTransformer |
|---|---|---|
| Token | a patch of one channel | the whole series of one variable |
| Attention across | patches in time | variables |
| Channels | independent | mixed by attention |
| Good when | many time steps, few relations | many related variables |

Which one is better depends on the data. Always test both against a linear baseline.

```check
{"q": "In iTransformer, what is one token?", "type": "single",
 "options": ["One time step of all variables", "The whole history of one variable", "One patch of one variable"], "answer": 1,
 "why": ["That is the classic layout.", "Correct: tokens are variates.", "That is PatchTST."]}
```

## Worked example

We (1) compute attention weights for 4 tokens. We (2) implement patching and compare token counts. We (3) show the two token layouts.

```python
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

# 1) scaled dot-product attention on 4 tokens with d = 2
rng = np.random.default_rng(0)
Q = rng.normal(size=(4, 2)); K = rng.normal(size=(4, 2)); V = rng.normal(size=(4, 2))
scores = Q @ K.T / np.sqrt(2)                        # [4, 4] table
weights = np.exp(scores) / np.exp(scores).sum(axis=1, keepdims=True)   # softmax per row
out = weights @ V                                    # weighted average of values
print("rows sum to 1:", weights.sum(axis=1).round(3))
print("output shape:", out.shape)

# 2) patching: 512 steps -> patches of 16 with stride 8, last value repeated 8 times at the end
x = np.arange(512.0)
padded = np.concatenate([x, np.repeat(x[-1], 8)])
patches = sliding_window_view(padded, 16)[::8]
print("patches:", patches.shape, "attention entries:", patches.shape[0] ** 2, "vs", 512 ** 2)
print("reduction factor:", 512 ** 2 // patches.shape[0] ** 2)

# 3) token layouts for 7 variables and 96 time steps
data = rng.normal(size=(96, 7))                      # [time, variables]
classic_tokens = data                                # 96 tokens, each with 7 numbers
inverted_tokens = data.T                             # 7 tokens, each with 96 numbers
print("classic:", classic_tokens.shape, "inverted:", inverted_tokens.shape)

# Output:
# rows sum to 1: [1. 1. 1. 1.]
# output shape: (4, 2)
# patches: (64, 16) attention entries: 4096 vs 262144
# reduction factor: 64
# classic: (96, 7) inverted: (7, 96)
```

## Common mistakes

- Believing "Transformer" means "better". Always run a seasonal naive and a linear baseline.
- Using a very long lookback with a model that was not designed for it.
- Mixing up patch length, stride and the number of patches.
- Using PatchTST (channel independent) and expecting it to learn relations between variables.
- Reporting results on a benchmark with a "drop last" setting in the test loader, which silently removes test samples. Check the evaluation code.

## Interview lens

**Typical question:** "Why is a plain Transformer a poor fit for long time series and how does PatchTST fix it?"

**Strong answer:** Self-attention costs n squared in the number of tokens. A single time step carries little meaning. So point-wise tokens are expensive and weak. PatchTST cuts each series into patches, for example length 16 with stride 8. A 512-step window becomes 64 tokens. Attention is then about 64 times cheaper. Each patch holds local shape, like a word. It also processes each channel independently with shared weights, which reduces overfitting. I would still compare it with a linear baseline and with seasonal naive on a time-based backtest.

**Red flags:** cannot explain patching; claims attention is linear in length; says iTransformer uses time steps as tokens.

## Real world

- Informer won a best paper award at AAAI 2021. PatchTST (ICLR 2023) and iTransformer (ICLR 2024) are common baselines in long-term forecasting papers.
- The patch idea was reused by later pre-trained models. For example, Google's TimesFM works on patches of the input series (stage 7).

## Staff lens

- **Standardize on a baseline ladder, not on a model.** Define a fixed order. Use seasonal naive, a linear model, boosted trees, then a deep model. A deep model is allowed in production only if it beats the ladder on a shared backtest, after cost.
- **Cost of ownership.** A Transformer needs GPUs for training and often for serving. It also needs a feature pipeline and people who can debug it. Count this in the decision.
- **Benchmark skepticism.** Public long-term benchmarks are small and used many times. Do not copy a paper's ranking into your platform. Rebuild the result on your own data.

## Key points

- Attention cost grows with the square of the number of tokens.
- Informer and Autoformer reduce cost or add decomposition; PatchTST uses patches (64 tokens for 512 steps) and channel independence.
- iTransformer makes each variable one token, so attention models relations between variables.
- Compare any Transformer with simple baselines before you trust it.
