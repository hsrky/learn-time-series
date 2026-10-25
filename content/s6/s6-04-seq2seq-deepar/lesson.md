---
id: s6-04-seq2seq-deepar
title: Seq2seq and DeepAR (probabilistic forecasts)
minutes: 30
level: intermediate
goals: [Explain the encoder-decoder idea and autoregressive forecasting, Describe how DeepAR predicts a distribution instead of one number, Compute the Gaussian negative log-likelihood]
prereqs: [s6-02-rnn-lstm-gru]
tags: [deepar, seq2seq, probabilistic, gluonts]
skills: [uncertainty, from-scratch]
---
## Warm-up

```check
{"q": "What does an LSTM forget gate with value 1 do?", "type": "single",
 "options": ["Erases the old memory", "Keeps the old memory", "Writes new memory"], "answer": 1,
 "why": ["That is a forget gate of 0.", "Correct: c is multiplied by 1.", "Writing is the input gate."]}
```

```check
{"q": "A quantile forecast at level 0.9 says:", "type": "single",
 "options": ["The value is 90% likely to be exactly this number.", "About 90% of outcomes should be at or below this number.", "The error is 90%."], "answer": 1,
 "why": ["Exact values have almost zero probability.", "Correct.", "Quantiles are values, not error rates."]}
```

## Why it matters

A forecast without uncertainty is half a forecast. A shop that stocks for the "average" demand runs out half the time. It needs the 90% quantile.
DeepAR is a famous deep model that gives a whole **distribution** for each future step. It was built at Amazon for forecasting demand of many products. It is a standard interview topic for "probabilistic deep learning".

## Seq2seq: encoder and decoder

A [[sequence-to-sequence]] (seq2seq) model has two parts:

1. The **encoder** reads the past window and squeezes it into a hidden state.
2. The **decoder** starts from that state and writes the future, one step at a time.

The decoder is **autoregressive**: the value it predicts at step t is fed back as the input of step t+1. This is the recursive strategy you know from classical forecasting.
During training, we usually feed the *real* previous value instead of the model's own guess. This is called [[teacher forcing]]. It makes training stable.
But at test time, the model must use its own guesses, so small errors can pile up. This gap between training and test is called *exposure bias*.

```check
{"q": "What is teacher forcing?", "type": "single",
 "options": ["Feeding the real previous value to the decoder during training.", "Forcing the model to predict zero.", "Training with a very high learning rate."], "answer": 0,
 "why": ["Correct.", "No.", "No, it is unrelated to the learning rate."]}
```

## DeepAR: a distribution at every step

DeepAR (Salinas, Flunkert, Gasthaus and Januschowski, Amazon) works like this:

- One LSTM is trained on **many related series at once** (a [[global model]]), for example thousands of products.
- At each step the network does not output a value. It outputs the **parameters** of a distribution: for a normal distribution, a mean `mu` and a spread `sigma`.
- For counts (like units sold), the paper uses a **negative binomial** distribution instead, which fits non-negative whole numbers.
- Each series is divided by its own scale, the average of its input window. This lets big and small series share one model. The output is scaled back.
- Inputs include the previous value, known covariates (like price or holiday) and a learned vector for each series (an *embedding*).

To get the forecast, DeepAR draws many **sample paths**. For each path, it samples a value from the distribution at step 1 and feeds it back. Then it samples at step 2, and so on. The quantiles of the sample paths are the probabilistic forecast.

```check
{"q": "Why does DeepAR divide each series by its own scale?", "type": "single",
 "options": ["So one model can learn from series with very different sizes.", "To make the plot prettier.", "Because LSTMs cannot read negative numbers."], "answer": 0,
 "why": ["Correct: a series with values near 10,000 and one near 5 would otherwise hurt training.", "Not the reason.", "LSTMs can read negative numbers."]}
```

## The loss: negative log-likelihood

How do we train a model that outputs a distribution? We ask: *"How likely is the real value under the predicted distribution?"* The model should give real values a high probability.
The [[likelihood]] is that probability (density). We take the logarithm and flip the sign, to get a loss to minimize: the [[negative log-likelihood]] (NLL).

For one point under a normal distribution:

`NLL = 0.5 · log(2π · σ²) + (y − μ)² / (2σ²)`

- `y`: the real value. `μ` (mu): the predicted mean. `σ` (sigma): the predicted spread, always positive.
- Second term: the squared error, divided by the spread. A big error is cheap when σ is big.
- First term: grows with σ. It punishes a model that says "I am never sure".

Example: error `y − μ = 1`. A very small σ = 0.25 gives NLL 7.53 (overconfident, big punishment). Next, σ = 1 gives 1.42 (the best). And σ = 3 gives 2.07 (too vague).

```chart
{"title": "NLL when the error is 1, for different sigma", "x": "sigma", "height": 220,
 "series": [{"name": "NLL", "x": [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0],
             "y": [7.533, 2.226, 1.52, 1.419, 1.462, 1.547, 1.642, 1.737, 1.829, 1.915, 1.997, 2.073]}],
 "caption": "The loss is lowest when sigma matches the real size of the error. The model learns honest uncertainty."}
```

The network outputs a raw number for σ. A *softplus* function, `log(1 + e^z)`, turns it into a positive σ.

```check
{"q": "Error = 0 and sigma = 1. NLL = 0.5·log(2π·1) = ?", "type": "numeric", "answer": 0.919, "tol": 0.005,
 "why": "log(2π) = log(6.283) = 1.838. Half of it is 0.919."}
```

## Point forecast vs distribution: what you gain

| | Point model (MSE) | DeepAR (NLL) |
|---|---|---|
| Output | one number | mean and spread, then samples |
| Prediction interval | needs extra work | comes from the samples |
| Good for | simple tracking | stock levels, capacity, risk |

The cost: you must check calibration. A 90% interval should contain the truth about 90% of the time (see the evaluation stage). A model with the wrong distribution type (for example a normal for counts that are mostly zero) gives poor intervals.

```check
{"q": "A model gives 80% intervals. On 100 test points, 55 fall inside. What is the problem?", "type": "single",
 "options": ["The intervals are too narrow (overconfident).", "The intervals are too wide.", "Nothing, 55 is fine."], "answer": 0,
 "why": ["Correct: coverage 55% is lower than 80%, so the model is too sure of itself.", "Too wide intervals would give coverage above 80%.", "The target was 80%."]}
```

## Worked example

We (1) score a prediction with the Gaussian NLL. We (2) draw sample paths from a tiny autoregressive model to get quantiles. There is no training here: the "model" is a fixed rule `mu(t) = 0.8·y(t−1) + 2`, `sigma = 0.5`.

```python
import numpy as np

# 1) Gaussian negative log-likelihood
def gaussian_nll(y, mu, sigma):
    return 0.5 * np.log(2 * np.pi * sigma**2) + (y - mu)**2 / (2 * sigma**2)

y, mu = 12.0, 11.0
for sigma in [0.25, 1.0, 3.0]:
    print("sigma", sigma, "NLL", round(float(gaussian_nll(y, mu, sigma)), 3))

# 2) autoregressive sampling: each sampled value is fed back as the next input
rng = np.random.default_rng(1)
n_paths, horizon = 2000, 5
last = np.full(n_paths, 10.0)           # last observed value, copied for every path
paths = np.zeros((n_paths, horizon))
for t in range(horizon):
    mu_t = 0.8 * last + 2.0             # the "network" predicts the mean from the previous value
    last = rng.normal(mu_t, 0.5)        # draw one sample per path
    paths[:, t] = last

q10, q50, q90 = np.percentile(paths, [10, 50, 90], axis=0)
print("q10", q10.round(2))
print("q50", q50.round(2))
print("q90", q90.round(2))
print("interval width grows:", (q90 - q10).round(2))

# Output:
# sigma 0.25 NLL 7.533
# sigma 1.0 NLL 1.419
# sigma 3.0 NLL 2.073
# q10 [9.35 9.17 9.06 9.05 8.98]
# q50 [ 9.99 10.   10.    9.98  9.99]
# q90 [10.64 10.81 10.9  10.9  11.01]
# interval width grows: [1.29 1.64 1.84 1.86 2.02]
```

The interval gets wider with the horizon. Each sampled value carries its own noise into the next step, so uncertainty adds up. This is how autoregressive models express growing uncertainty.

## Common mistakes

- Using a normal distribution for non-negative counts with many zeros. Use a count distribution (negative binomial).
- Only reporting the mean of DeepAR and ignoring the quantiles.
- Not checking calibration (coverage) on a time-based test set.
- Training on one series only. DeepAR is built for many related series.
- Forgetting to un-scale the output with the series scale.

## Interview lens

**Typical question:** "How does DeepAR produce a probabilistic forecast?"

**Strong answer:** DeepAR trains one autoregressive LSTM across many series. At each step it outputs the parameters of a distribution. This can be the mean and spread of a normal, or a negative binomial for counts. It is trained by minimizing the negative log-likelihood of the real values. At forecast time it draws many sample paths and feeds each sample back as input. It reads the quantiles from the samples. I would check calibration with coverage and the pinball loss. I would compare against a seasonal naive and a boosted-tree baseline with quantile loss.

**Red flags:** saying DeepAR outputs only a mean; not knowing the loss is a likelihood; ignoring scale differences between series. Another is claiming intervals are correct without measuring coverage.

## Real world

- DeepAR was published by Amazon researchers (Salinas et al.). It appeared first on arXiv in 2017, then in the International Journal of Forecasting in 2020.
- It is available in GluonTS, an open-source toolkit from AWS, and as a built-in algorithm in Amazon SageMaker.
- The Amazon Chronos models (see stage 7) continue this line of work with a different design.

## Key points

- Seq2seq: an encoder reads the past, a decoder writes the future, step by step (autoregressive).
- DeepAR is one global LSTM that outputs distribution parameters, trained with negative log-likelihood.
- Sample paths give quantiles; the interval grows with the horizon.
- Always check calibration, and use the right distribution for the data (normal vs count).
