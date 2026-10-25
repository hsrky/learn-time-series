---
id: s6-06-temporal-fusion-transformer
title: Temporal Fusion Transformer (TFT)
minutes: 30
level: intermediate
goals: [Sort inputs into static, known-future and observed-past, Explain variable selection and gating in simple words, Explain quantile outputs and how TFT is interpretable]
prereqs: [s6-04-seq2seq-deepar]
tags: [tft, attention, quantile, interpretability]
skills: [uncertainty, production]
---
## Warm-up

```check
{"q": "A store's price for next week is already set by the company. In a forecasting model, what kind of input is it?", "type": "single",
 "options": ["Known in the future", "Only observed in the past", "Static"], "answer": 0,
 "why": ["Correct: the price is planned, so you know it for the whole horizon.", "Past-only inputs are unknown in the future, like tomorrow's weather observation.", "Static inputs never change, like store id."]}
```

```check
{"q": "The pinball loss for quantile 0.9 punishes which error more?", "type": "single",
 "options": ["Forecast too high", "Forecast too low", "Both the same"], "answer": 1,
 "why": ["For q = 0.9 the low side gets weight 0.9 and the high side 0.1.", "Correct: the 0.9 quantile should be high, so being below the truth costs more.", "Only at q = 0.5 are they the same."]}
```

## Why it matters

Real forecasting problems have many kinds of inputs: the store, the holiday calendar, the planned price, last week's sales, the weather you observed. Simple models mix them all together.
The **Temporal Fusion Transformer** (Lim, Arik, Loeff and Pfister; Google Cloud AI and Oxford; 2019 preprint, published in the International Journal of Forecasting, 2021) was designed for exactly this case: multi-horizon forecasts with mixed inputs, quantile outputs, and a way to see what the model used.

## Three kinds of input

TFT asks you to sort every input into one of three groups. This is good practice for any model, because it prevents leakage.

| Type | Meaning | Example |
|---|---|---|
| **Static** | does not change over time | store id, product category, region |
| **Known future** | you know it for the whole horizon | day of week, holiday, planned price, promotion |
| **Observed past** | known only until now | past sales, past temperature, past traffic |

Using an observed-past input in the future part of the model is leakage (you would use a value you do not have yet).

```check
{"q": "Which input is observed-past only?", "type": "single",
 "options": ["Day of week", "Yesterday's actual sales", "Product category"], "answer": 1,
 "why": ["The calendar is known in advance.", "Correct: future sales are exactly what you want to predict.", "Category is static."]}
```

## Building blocks, in plain words

- **[[Gated residual network]] (GRN):** a small block that can turn itself down. A [[gate]] (a number between 0 and 1) lets it skip its own work when the input is already good enough. This helps with small or noisy data.
- **[[Variable selection]]:** for each time step, the model learns a weight for each input feature (the weights sum to 1). Useless features get small weights. You can read these weights later.
- **Static covariate encoders:** the static inputs are turned into vectors that set the initial state of the LSTM and condition the other blocks. So "store A" and "store B" can behave differently.
- **LSTM encoder-decoder:** an LSTM reads the past and another one reads the known future. It handles local, short-range order.
- **Interpretable multi-head [[attention]]:** a layer that lets each future step look at *any* past step and weigh it. This captures long-range patterns, like "same day last week". TFT shares the value weights across heads, so the attention weights can be averaged and read.

```check
{"q": "What does the variable selection step output for each feature?", "type": "single",
 "options": ["A weight between 0 and 1 (all weights sum to 1)", "A forecast", "A random mask"], "answer": 0,
 "why": ["Correct: a softmax over features. You can inspect these as importance.", "Forecasts come at the end.", "The weights are learned, not random."]}
```

## Quantile outputs

TFT does not output one number. It outputs several [[quantile]]s per future step, for example the 10%, 50% and 90% values. It trains with the **pinball loss** (also called quantile loss), summed over the quantiles.

For quantile `q`, true value `y` and forecast `f`, with `e = y − f`:

`loss = max(q·e, (q − 1)·e)`

Example: y = 100, f = 90, so e = 10. For q = 0.9 the loss is 0.9·10 = 9. For q = 0.1 it is 1.
If instead f = 110 (e = −10): for q = 0.9 the loss is (0.9 − 1)·(−10) = 1; for q = 0.1 it is (0.1 − 1)·(−10) = 9.

So each output is pushed to be above the truth about 90% / below it about 10% of the time. The 10% and 90% outputs together form an 80% prediction interval.

```chart
{"title": "Quantile forecast: a median and an 80% band", "x": "step", "height": 220,
 "series": [
   {"name": "median (q50)", "gen": [["trend", {"slope": 0.3, "start": 50}], ["season", {"period": 12, "amp": 5}]], "n": 48},
   {"name": "q90", "gen": [["trend", {"slope": 0.3, "start": 56}], ["season", {"period": 12, "amp": 5}]], "n": 48, "dash": true},
   {"name": "q10", "gen": [["trend", {"slope": 0.3, "start": 44}], ["season", {"period": 12, "amp": 5}]], "n": 48, "dash": true}
 ],
 "caption": "A good model has about 80% of the real values between q10 and q90."}
```

## What is interpretable?

TFT is called interpretable because you can look at three things after training:

1. **Variable importance:** the average variable-selection weights, per input group.
2. **Attention over time:** which past steps the model looked at. A peak every 7 steps means it found a weekly pattern.
3. **Event effects:** compare the forecast with and without a known event.

Be careful: attention weights show where the model looked, not a proof of cause. Say "the model relies on" and not "this causes".

```check
{"q": "A stakeholder says 'the attention peak shows that holidays CAUSE the sales jump'. Your answer?", "type": "single",
 "options": ["Agreed, attention is causal proof.", "Attention shows what the model uses, not a proven cause; check with experiments.", "Attention is random."], "answer": 1,
 "why": ["Attention is not a causal test.", "Correct.", "It is learned and informative, but not causal."]}
```

## Worked example

We code two small pieces in numpy: variable selection weights, and the pinball loss for three quantiles.

```python
import numpy as np

# --- variable selection: 3 features at one time step, each already embedded in a vector of size 4
rng = np.random.default_rng(0)
emb = rng.normal(size=(3, 4))            # rows: price, promo, temperature
scores = np.array([2.0, 1.0, -1.0])      # in TFT these come from a small network
w = np.exp(scores) / np.exp(scores).sum()   # softmax: positive, sums to 1
mixed = (w[:, None] * emb).sum(axis=0)      # weighted sum = the input to the next layer
print("feature weights:", w.round(3), "sum =", w.sum().round(3))
print("mixed vector shape:", mixed.shape)

# --- pinball loss for quantiles 0.1, 0.5, 0.9
def pinball(y, f, q):
    e = y - f
    return np.maximum(q * e, (q - 1) * e)

y = 100.0
for f in [90.0, 110.0]:
    print("forecast", f, [round(float(pinball(y, f, q)), 2) for q in (0.1, 0.5, 0.9)])

# --- coverage of an 80% band on 1000 simulated outcomes with a well-calibrated model
outcomes = rng.normal(100, 10, size=1000)
lo, hi = 100 - 1.2816 * 10, 100 + 1.2816 * 10     # true 10% and 90% quantiles of N(100, 10)
print("coverage:", float(((outcomes >= lo) & (outcomes <= hi)).mean()))

# Output:
# feature weights: [0.705 0.259 0.035] sum = 1.0
# mixed vector shape: (4,)
# forecast 90.0 [1.0, 5.0, 9.0]
# forecast 110.0 [9.0, 5.0, 1.0]
# coverage: 0.814
```

For `f = 90` (too low) the 0.9 quantile pays 9.0. For `f = 110` (too high) the 0.1 quantile pays 9.0. Each quantile dislikes the error on its "wrong" side.

```notebook
# Run with PyTorch Forecasting (check the docs of your installed version; API names may change)
from pytorch_forecasting import TimeSeriesDataSet, TemporalFusionTransformer
from pytorch_forecasting.metrics import QuantileLoss

# data: columns store_id, time_idx, sales, price, promo, day_of_week
training = TimeSeriesDataSet(
    data, time_idx="time_idx", target="sales", group_ids=["store_id"],
    max_encoder_length=56, max_prediction_length=14,
    static_categoricals=["store_id"],
    time_varying_known_reals=["price", "promo", "time_idx"],
    time_varying_known_categoricals=["day_of_week"],
    time_varying_unknown_reals=["sales"],
)
tft = TemporalFusionTransformer.from_dataset(training, hidden_size=32, attention_head_size=4,
                                             loss=QuantileLoss([0.1, 0.5, 0.9]))
```

## Common mistakes

- Putting a past-only feature in the "known future" group (leakage).
- Skipping baselines. TFT has many parts and needs enough data; on small data, seasonal naive or LightGBM can win.
- Reading attention as causal proof.
- Using only the median and ignoring q10/q90.
- Not checking calibration (coverage) of the quantiles on a later time period.

## Interview lens

**Typical question:** "When would you use a Temporal Fusion Transformer, and what is special about it?"

**Strong answer:** TFT fits multi-horizon forecasting with mixed inputs: static data like store id, known-future data like holidays and planned prices, and observed-past data like sales. It uses variable selection networks and gated residual networks to ignore useless inputs, an LSTM for local patterns, and interpretable multi-head attention for long-range patterns. It outputs quantiles trained with the pinball loss, so I get prediction intervals. I can inspect variable importance and attention patterns, but I treat them as hints, not proof. I would only choose it if it beats a seasonal naive and a boosted-tree baseline on a time-based backtest, because it costs more to train and serve.

**Red flags:** cannot name the three input types; thinks TFT outputs a single value; says attention proves causality.

## Real world

- The TFT paper reported results on electricity, traffic, retail (Favorita) and volatility data sets and compared with DeepAR, MQRNN and other models.
- TFT is implemented in PyTorch Forecasting, in Darts, in NeuralForecast, and in GluonTS.

## Key points

- Sort inputs: static, known-future, observed-past. Never use observed-past in the future.
- TFT uses gating, variable selection, an LSTM and interpretable attention.
- It outputs quantiles trained with the pinball loss, giving prediction intervals.
- Interpretation shows what the model uses, not proven causes.
