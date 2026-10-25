---
id: s6-05-nbeats-nhits
title: N-BEATS and N-HiTS
minutes: 30
level: intermediate
goals: [Explain backcast, forecast and residual stacking, Describe trend and seasonality basis functions, Explain what N-HiTS changes for long horizons]
prereqs: [s6-01-windowed-datasets]
tags: [nbeats, nhits, mlp, basis-expansion]
skills: [from-scratch, baseline-first]
---
## Warm-up

```check
{"q": "A window has input length 24 and horizon 12. What shapes do X and y have for one example?", "type": "single",
 "options": ["X: 24 values, y: 12 values", "X: 12 values, y: 24 values", "Both 36 values"], "answer": 0,
 "why": ["Correct: the input is the past (24), the target is the future (12).", "Reversed.", "36 is the length of the whole frame."]}
```

```check
{"q": "What is a residual?", "type": "single",
 "options": ["The part of the data that a model did not explain: data minus fit.", "A random seed.", "The learning rate."], "answer": 0,
 "why": ["Correct.", "No.", "No."]}
```

## Why it matters

In 2018 the M4 competition (100,000 series) was won by a hybrid of exponential smoothing and a recurrent network. In 2019, the N-BEATS paper appeared (Oreshkin et al., Element AI and ServiceNow; ICLR 2020). It used **plain fully connected layers**, with no recurrence and no attention. The authors reported better results than the M4 winner on the M4 data.
The idea is simple, strong and easy to explain, so interviewers like it. Its relative N-HiTS (2023) is a common baseline for long-horizon forecasting.

## The block: backcast and forecast

An N-BEATS **block** is a small stack of fully connected layers (an MLP). It reads the input window and produces **two** outputs:

- a [[backcast]]: its best reconstruction of the input window (the past it can explain),
- a **forecast**: its contribution to the future.

Example with numbers. The input is `[10, 12, 14, 16]`. A first block explains the rising line and says: backcast `[10, 12, 14, 16]`. Nothing is left. The forecast contribution is `[18, 20]` (the line continues).

## Residual stacking

Blocks are chained. Each block gets the **residual** of the previous one: the input minus what the earlier blocks have already explained.

```
r(0) = input window
for each block k:
    backcast(k), forecast(k) = block_k( r(k−1) )
    r(k) = r(k−1) − backcast(k)
final forecast = sum of all forecast(k)
```

It is like peeling an onion. The first block removes the main pattern. Later blocks work on what is left. The final forecast is the **sum** of the pieces. Many blocks form a *stack*; the full model has several stacks.

```check
{"q": "How is the final N-BEATS forecast built?", "type": "single",
 "options": ["Only the last block's forecast.", "The sum of the forecasts of all blocks.", "The average of the backcasts."], "answer": 1,
 "why": ["Earlier blocks also contribute.", "Correct: each block adds a piece.", "Backcasts are only used to compute residuals."]}
```

## Basis expansion: make the blocks interpretable

Instead of letting the MLP output free numbers, we can force it to output a few **coefficients** `theta`. The curve is then `theta` times fixed **basis functions** (a [[basis function]] is a ready-made shape).

- **Trend block:** basis = polynomials `1, t, t², ...` (low degree). Output is a smooth curve.
- **Seasonality block:** basis = sines and cosines at fixed periods (Fourier terms). Output is a repeating pattern.
- **Generic block:** no fixed basis. The network learns its own shapes (usually more accurate, less interpretable).

Trend and seasonal blocks give separate pieces. So you can plot "the trend part" and "the seasonal part" of a forecast. This is the *interpretable* N-BEATS configuration.

```chart
{"title": "Forecast = trend piece + season piece", "x": "step", "height": 220,
 "series": [
   {"name": "trend piece", "gen": [["trend", {"slope": 0.5, "start": 10}]], "n": 36},
   {"name": "season piece", "gen": [["season", {"period": 12, "amp": 3}]], "n": 36, "dash": true},
   {"name": "sum (forecast)", "gen": [["trend", {"slope": 0.5, "start": 10}], ["season", {"period": 12, "amp": 3}]], "n": 36}
 ],
 "marks": [{"x": 24, "label": "forecast starts"}],
 "caption": "Stacked blocks add up: a trend block gives the line, a seasonal block gives the repeating wave."}
```

```check
{"q": "Which basis would you use for a block that should model a repeating weekly pattern?", "type": "single",
 "options": ["Low-degree polynomials", "Fourier terms (sines and cosines) with period 7", "A constant"], "answer": 1,
 "why": ["Polynomials are smooth and do not repeat.", "Correct: Fourier terms repeat with the chosen period.", "A constant has no shape."]}
```

## N-HiTS: look at several time scales

N-HiTS (Challu et al., AAAI 2023) keeps the N-BEATS structure and changes two things, aimed at **long horizons**:

1. **Multi-rate input sampling:** each stack first applies *pooling* (it shrinks the input by taking the max over small groups). Early stacks use big pooling and see slow patterns; later stacks use small pooling and see fast patterns.
2. **Hierarchical interpolation:** a block predicts only a few points of its forecast. A simple interpolation fills in the rest. Fewer outputs means fewer parameters.

Result: the paper reports better accuracy than several Transformer models on long-horizon benchmarks, and much lower compute. N-HiTS is available in the NeuralForecast library (Nixtla).

```check
{"q": "What is the purpose of pooling at the start of an N-HiTS stack?", "type": "single",
 "options": ["Let the stack focus on slower, large-scale patterns and use fewer parameters.", "Remove the residuals.", "Make the output positive."], "answer": 0,
 "why": ["Correct: coarser input means the block sees the big picture.", "Residuals are still used.", "Not related."]}
```

## Worked example

We build a tiny, training-free version of the stacking idea. The "network" of each block is replaced by a least-squares fit onto a basis. A trend block runs first, a seasonal block runs on the residual, and we sum the forecasts.

```python
import numpy as np

L, H = 24, 12                                   # backcast length, forecast length
t = np.arange(L + H)
series = 10 + 0.5 * t + 3 * np.sin(2 * np.pi * t / 12)   # trend + season of period 12
x, future = series[:L], series[L:]

def poly_basis(tt, degree):                     # trend basis: 1, t, t^2 ... (t scaled to [0, 1+])
    return np.stack([(tt / L) ** p for p in range(degree + 1)], axis=1)

def fourier_basis(tt, period, harmonics):       # season basis: sin and cos
    cols = []
    for k in range(1, harmonics + 1):
        cols += [np.sin(2 * np.pi * k * tt / period), np.cos(2 * np.pi * k * tt / period)]
    return np.stack(cols, axis=1)

def block(residual, basis_fn):
    B = basis_fn(t)                                         # [L+H, n_coef]
    theta, *_ = np.linalg.lstsq(B[:L], residual, rcond=None)  # the "network output": coefficients
    return B[:L] @ theta, B[L:] @ theta                     # backcast, forecast

r = x.copy()
total = np.zeros(H)
print("input std:", round(float(r.std()), 3))
for name, fn in [("trend", lambda tt: poly_basis(tt, 1)), ("season", lambda tt: fourier_basis(tt, 12, 1))]:
    back, fore = block(r, fn)
    r = r - back                                            # residual goes to the next block
    total += fore                                           # forecasts are added
    print(name, "block: residual std after =", round(float(r.std()), 3))

naive = np.full(H, x[-1])
print("MAE N-BEATS-style:", round(float(np.abs(future - total).mean()), 3))
print("MAE naive (last value):", round(float(np.abs(future - naive).mean()), 3))

# Output:
# input std: 3.299
# trend block: residual std after = 1.961
# season block: residual std after = 0.743
# MAE N-BEATS-style: 2.103
# MAE naive (last value): 4.75
```

The spread of the residual falls with each block. The stacked forecast has less than half the error of the naive forecast. The rest of the error appears because the blocks are fitted one after another. The trend block takes a little of the seasonal wave. A real network trains all blocks together. That is residual stacking.

```notebook
# Real N-BEATS / N-HiTS training uses the NeuralForecast library (Nixtla). Check the docs for your installed version.
import pandas as pd
from neuralforecast import NeuralForecast
from neuralforecast.models import NHITS

# df has columns: unique_id, ds (date), y
nf = NeuralForecast(models=[NHITS(h=24, input_size=96, max_steps=500)], freq="h")
nf.fit(df=df)
forecast = nf.predict()
```

## Common mistakes

- Comparing N-BEATS with a weak baseline, or without a seasonal naive and an exponential smoothing baseline.
- Using an input window too short to contain one full season.
- Training one model per series for a few series. These models shine with many series.
- Treating the interpretable version as a free explanation: the blocks are only interpretable as far as the chosen basis is.
- Forgetting that random seeds matter; the paper uses an ensemble of many models, which costs compute.

## Interview lens

**Typical question:** "Explain the N-BEATS architecture."

**Strong answer:** N-BEATS is a deep stack of fully connected blocks. Each block reads a window and outputs a backcast and a forecast. The backcast is subtracted from the input. The next block works on the residual. All the forecasts are summed. A block can output coefficients for a trend (polynomial) or seasonal (Fourier) basis, which makes the forecast interpretable. The paper reported strong results on M3, M4 and Tourism data, using ensembles. N-HiTS adds multi-rate pooling and hierarchical interpolation for long horizons.

**Red flags:** thinking N-BEATS uses attention or recurrence; not knowing what the backcast is for; claiming it beats everything everywhere.

## Real world

- N-BEATS was evaluated on the M3, M4 and Tourism datasets in the original paper. Its authors report a clear improvement over the M4 winning entry.
- N-BEATS and N-HiTS are implemented in Nixtla's NeuralForecast and also in the Darts library.

## Key points

- A block reads a window and outputs a backcast and a forecast.
- Residual stacking: input minus backcast goes to the next block; the final forecast is the sum.
- Trend (polynomial) and season (Fourier) bases give an interpretable version.
- N-HiTS adds multi-rate pooling and hierarchical interpolation for cheaper long-horizon forecasts.
