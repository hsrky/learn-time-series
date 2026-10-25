---
id: s11-03-deepar-gluonts-chronos
title: Amazon: DeepAR, GluonTS and Chronos
minutes: 25
level: advanced
goals: [Explain how DeepAR forecasts a distribution with one RNN trained on many series, Describe how Chronos turns numbers into tokens, Compare a classical per-series model with a global neural model]
prereqs: [s11-02-prophet-at-facebook]
tags: [deepar, gluonts, chronos, foundation-model, probabilistic]
skills: [case-studies, deep-learning-ts, probabilistic-forecasting]
---

## Warm-up

```check
{"q": "Prophet writes the series as...", "type": "single",
 "options": ["trend + seasonality + holidays + error", "AR + MA", "Only lag features"],
 "answer": 0,
 "why": ["Correct.", "That is ARIMA.", "That is a feature-based ML model."]}
```

```check
{"q": "Why does a global model help with a new product that has 10 days of history?", "type": "single",
 "options": ["It memorises the product", "It uses patterns learned from many similar series", "It ignores the history"],
 "answer": 1,
 "why": ["There is nothing to memorise.", "Correct.", "It uses the history, but not only it."]}
```

## Why it matters

Amazon sells millions of items. Demand for each item is a time series, and most items have short or sparse history. Per-item models fail on such data. Amazon researchers built **[[DeepAR]]** to train one neural network on all related series. It outputs not one number but a **distribution**, because planners need to see risk. Later, the same group asked a bigger question. Can one pretrained model (a **[[foundation model]]**) forecast new series it has never seen? The result is **Chronos**.

## DeepAR: one RNN, many series, a distribution as output

DeepAR was described by Salinas, Flunkert, Gasthaus and Januschowski. The paper is from 2017 and was published in the International Journal of Forecasting in 2020. It works like this:

1. **One recurrent network (LSTM)** is trained on *all* series together.
2. At each step it reads the previous value, covariates and an **item embedding**. The covariates are calendar, price and promotion. The embedding is a learned vector for each series.
3. It does not output a value. It outputs the **parameters of a distribution**. For a Gaussian these are the mean and standard deviation. For count data such as sales units it can output the parameters of a **[[negative binomial]]**.
## How DeepAR trains and forecasts

The next three steps cover training, forecasting and scaling.

4. Training maximises the likelihood of the real values (minimises the **negative log-likelihood**, NLL).
5. To forecast, it **samples** the next value, feeds it back, and repeats. Many sample paths give any quantile you need.
6. Each series is **scaled** by its own average level so that big and small items can share one model.

```check
{"q": "Why does DeepAR output distribution parameters and not a single value?", "type": "single",
 "options": ["To use less memory", "So that it can give quantiles and uncertainty for decisions", "Because LSTMs cannot output a number", "To avoid scaling"],
 "answer": 1,
 "why": ["Memory is not the reason.", "Correct: planners need prediction intervals and quantiles, like in the newsvendor problem.", "They can output numbers.", "Scaling is still used."]}
```

```check
{"q": "Which output distribution suits daily unit sales (small non-negative integers)?", "type": "single",
 "options": ["Gaussian", "Negative binomial", "Uniform on [0, 1]", "Student-t with negative values"],
 "answer": 1,
 "why": ["A Gaussian allows negative and non-integer values.", "Correct: it models counts and is flexible about spread.", "Sales are not limited to 0-1.", "Negative sales are not meaningful."]}
```

## GluonTS

**[[GluonTS]]** is Amazon's open-source toolkit for probabilistic time-series modelling (Alexandrov et al., 2020). It gives you datasets, standard models (DeepAR and others), evaluation of quantile forecasts, and tools to build new models. It was first built on MXNet, and later versions support PyTorch. Many later tools reuse its data formats and metrics. Examples are the long "item, time, target" layout and the weighted quantile loss.

## Chronos: time series as language

**Chronos** (Ansari et al., 2024, Amazon) pretrains a language-model architecture on time series. The key trick is the **[[tokenizer]]**:

1. **Scale** the series: divide by the mean absolute value of the context, so the numbers are around 1.
2. **Quantise**: cut the range into many equal bins (Chronos uses thousands). Replace each value by its bin number, the **token**.
3. Train a standard T5-style model to predict the next token with ordinary cross-entropy loss.
4. To forecast: sample token sequences, convert tokens back to values, and multiply by the scale. Many samples give a distribution.

It was trained on a large collection of public datasets plus **synthetic** series, made with Gaussian processes. It works **[[zero-shot]]**: it forecasts new series with no training on them. Faster variants such as Chronos-Bolt appeared later. Chronos models are available in AutoGluon-TimeSeries and on public model hubs.

```widget
{"name": "chronos-tokens", "params": {}}
```

```check
{"q": "What is the purpose of scaling by the mean absolute value before tokenising?", "type": "single",
 "options": ["To remove seasonality", "To make series of different sizes use the same range of tokens", "To make the model smaller", "To add noise"],
 "answer": 1,
 "why": ["Scaling does not remove seasonality.", "Correct: big and small series then share one vocabulary.", "Model size is unchanged.", "It adds no noise."]}
```

## Which one to use?

| | Per-series ETS/ARIMA | DeepAR | Chronos (zero-shot) |
|---|---|---|---|
| Training | Per series, quick | Hours on many series | None (pretrained) |
| Many related series | Ignores relations | Learns shared patterns | Uses patterns from pretraining |
| Covariates (price, promo) | Limited | Yes | Basic versions: mostly target only |
| Uncertainty | Model intervals | Sample paths | Sample paths |
| Risk | Weak on short data | Needs tuning and data | Can be wrong on unusual series |

A safe rule: **compare with seasonal naive and ETS on your own backtest**. Zero-shot models are an excellent first baseline because they need no training.

## Worked example

We write a tiny version of the Chronos tokenizer. It scales, quantises into 201 bins between −3 and +3, and converts back.

```python
import numpy as np

context = np.array([120, 135, 150, 142, 128, 160, 175, 168], dtype=float)

scale = np.mean(np.abs(context))                  # 1) mean-absolute scaling
scaled = context / scale

n_bins, lo, hi = 201, -3.0, 3.0                   # 2) uniform bins on [-3, 3]
edges = np.linspace(lo, hi, n_bins + 1)
tokens = np.clip(np.digitize(scaled, edges) - 1, 0, n_bins - 1)

centers = (edges[:-1] + edges[1:]) / 2            # 3) token -> value
restored = centers[tokens] * scale

print("scale:", round(float(scale), 2))
print("tokens:", tokens.tolist())
print("restored:", np.round(restored, 1).tolist())
print("max error:", round(float(np.max(np.abs(restored - context))), 1))
# Output:
# scale: 147.25
# tokens: [127, 131, 134, 132, 129, 136, 140, 138]
# restored: [118.7, 136.3, 149.4, 140.7, 127.5, 158.2, 175.8, 167.0]
# max error: 1.8
```

Each real value became a small integer, a "word". A language model can now predict the next word. The restore step shows the cost: the quantisation error. Chronos uses many more bins, so the error is small.

## Common mistakes

- Calling Chronos "just an LLM". It uses a language-model architecture, but it is trained on time series with a special tokenizer.
- Expecting zero-shot to win on every dataset. Test it.
- Using DeepAR on a handful of series. It needs many related series.
- Evaluating probabilistic forecasts with MAE only. Use quantile loss (CRPS-like) and coverage.
- Forgetting scaling, so large series dominate the loss.

## Interview lens

**Typical question:** "What is DeepAR, and how is Chronos different?"

**Strong answer:** DeepAR is an autoregressive RNN trained across many related series. It outputs the parameters of a distribution, for example negative binomial for counts. It is trained by maximum likelihood with per-series scaling. Forecasts come from sampling paths. Chronos is a pretrained foundation model. It scales and quantises values into tokens. It trains a T5-style model with cross-entropy on a large corpus of real and synthetic series. It forecasts zero-shot by sampling tokens. DeepAR needs training on your data and supports covariates well; Chronos needs no training and is a strong baseline. I would compare both with seasonal naive and ETS on a rolling backtest.

**Red flags:** Not knowing that the output is a distribution. Saying foundation models make baselines unnecessary.

## Real world

Amazon developed DeepAR and described it in a public paper. There are implementations in GluonTS and in Amazon's forecasting services. The Chronos paper, "Chronos: Learning the Language of Time Series", and its model weights were released publicly in 2024. Both come from Amazon research teams, and both are available as open-source code.

## Key points

- DeepAR: one RNN for many series, outputs distribution parameters, trained by likelihood, forecasts by sampling.
- GluonTS: Amazon's open-source toolkit for probabilistic forecasting.
- Chronos: scale and quantise values into tokens, train a T5-style model, forecast zero-shot by sampling.
- Global models help short and sparse series; zero-shot models are strong, cheap baselines.
- Always validate against seasonal naive and ETS on your own data.
