---
id: s6-03-tcn-causal-convolutions
title: TCN and dilated causal convolutions
minutes: 25
level: intermediate
goals: [Explain a causal convolution and why it never sees the future, Use dilation to grow the receptive field fast, Compute the receptive field of a stack of layers]
prereqs: [s6-02-rnn-lstm-gru]
tags: [tcn, convolution, wavenet, deep-learning]
skills: [from-scratch]
---
## Warm-up

```check
{"q": "Why is an RNN slow to train on long sequences?", "type": "single",
 "options": ["Its steps depend on each other and run in order.", "It has no weights.", "It cannot use a GPU at all."], "answer": 0,
 "why": ["Correct: step t needs the hidden state of step t−1.", "It has weights.", "It can use a GPU, but the time steps are still sequential."]}
```

```check
{"q": "Which tensor shape is the usual layout for time series input?", "type": "single",
 "options": ["[batch, time, features]", "[time, batch, batch]", "[features, features, time]"], "answer": 0,
 "why": ["Correct.", "Not a valid layout.", "Not a valid layout."]}
```

## Why it matters

RNNs read time step by step. A **convolution** looks at many time steps *at once*, so the GPU can process the whole series in parallel.
The Temporal Convolutional Network (TCN) is a stack of convolutions made safe for forecasting. It is fast, stable to train, and a strong baseline in many sequence tasks.
The same building block powers WaveNet (audio) and appears inside several forecasting models.

## Convolution in one picture

A [[convolution]] slides a small list of weights, the **kernel**, along the series. At each position, it multiplies the kernel with the values under it and adds them up.

Example. Series `1 2 3 4`. Kernel `[1, 1]` (kernel size 2). Output at each time = current value + previous value:

| t | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| x | 1 | 2 | 3 | 4 |
| y | 1 | 3 | 5 | 7 |

At t = 0 there is no previous value. We treat it as 0 (this is **padding** on the left). This output only used the present and the past. That is a [[causal convolution]].
A normal convolution with symmetric padding also looks at the future. For forecasting, that would be cheating: **leakage**. So a TCN pads only on the left.

```check
{"q": "Series 2 4 6 8, kernel [1, 1], causal, zero padding on the left. What is the output at t = 2?", "type": "numeric", "answer": 10, "tol": 0,
 "why": "y[2] = x[2] + x[1] = 6 + 4 = 10."}
```

## Dilation: see far with few layers

With kernel size 2 and no tricks, one layer sees 2 steps. To see 100 steps you would need about 100 layers. **Dilation** fixes this. A dilation `d` means the kernel skips `d − 1` values between taps.

- Dilation 1: looks at `t, t−1`.
- Dilation 2: looks at `t, t−2`.
- Dilation 4: looks at `t, t−4`.

Stack layers with dilations 1, 2, 4, 8, ... Each layer doubles how far back the network can see.

```chart
{"title": "Receptive field grows with the number of layers (kernel 2, dilations 1, 2, 4, ...)", "x": "layers", "height": 200,
 "series": [{"name": "receptive field", "kind": "bar", "y": [2, 4, 8, 16, 32, 64, 128, 256]}],
 "caption": "8 layers see 256 steps. Without dilation, 8 layers of kernel 2 would see only 9."}
```

## Receptive field formula

The [[receptive field]] is the number of past steps (including the present) that can change one output value.

`RF = 1 + (k − 1) · (d1 + d2 + ... + dL)`

- `k`: kernel size.
- `d1 ... dL`: the dilation of each of the L layers.

Check: `k = 2`, dilations 1, 2, 4, 8 gives `1 + 1·15 = 16`.
Check: `k = 3`, dilations 1, 2, 4, 8 gives `1 + 2·15 = 31`.

If your input window is 96 steps, make sure `RF` is about 96 or more. If it is smaller, part of the window is never used.

```check
{"q": "Kernel size 3, dilations 1, 2, 4, 8, 16. What is the receptive field?", "type": "numeric", "answer": 63, "tol": 0,
 "why": "Sum of dilations = 31. RF = 1 + (3 − 1)·31 = 63."}
```

## Residual blocks and the full TCN

A TCN block has a causal dilated conv, ReLU, dropout, a second conv, and a **residual connection**. The block input is added to its output. [[Residual connection]]s let the signal and the training gradient flow through deep stacks. This fixes the vanishing gradient problem from the last lesson.

TCN vs RNN, from the original TCN paper (Bai, Kolter and Koltun, 2018):

| | RNN / LSTM | TCN |
|---|---|---|
| Parallel over time | No | Yes |
| Memory length | Unclear, learned | Fixed, known: the receptive field |
| Training | Can be unstable | Usually stable |
| Inference per step | Cheap (one cell) | Needs the last RF values |

The paper reported that a simple TCN beat typical LSTMs on several sequence benchmarks. Treat this with care: the result depends on the tasks and settings.

```check
{"q": "Which is an advantage of a TCN over an LSTM?", "type": "single",
 "options": ["Training can run in parallel over time steps.", "It has unlimited memory.", "It needs no input window."], "answer": 0,
 "why": ["Correct: convolutions over all positions run at the same time.", "Its memory is fixed by the receptive field.", "It still needs an input window."]}
```

## Worked example

We apply causal convolutions with numpy. We watch the receptive field with an **impulse**, a series that is 1 at one step and 0 elsewhere.

```python
import numpy as np

def causal_conv1d(x, w, dilation=1):
    # y[t] = sum_j w[j] * x[t - j*dilation]; missing past values count as 0
    n = len(x)
    y = np.zeros(n)
    for j, wj in enumerate(w):
        shift = j * dilation
        if shift >= n:
            break
        y[shift:] += wj * x[:n - shift]
    return y

def receptive_field(k, dilations):
    return 1 + (k - 1) * sum(dilations)

# 1) the small example from the text
print(causal_conv1d(np.array([1., 2., 3., 4.]), np.array([1., 1.])))

# 2) a stack of 3 layers, kernel [1, 1], dilations 1, 2, 4
x = np.zeros(16)
x[2] = 1.0                       # impulse at t = 2
h = x
for d in [1, 2, 4]:
    h = causal_conv1d(h, np.array([1., 1.]), dilation=d)
print("impulse response:", h.astype(int))
print("steps affected by the impulse:", int((h > 0).sum()))
print("receptive field:", receptive_field(2, [1, 2, 4]))
print("first affected step:", int(np.argmax(h > 0)), "(never before 2: no future leak)")

# Output:
# [1. 3. 5. 7.]
# impulse response: [0 0 1 1 1 1 1 1 1 1 0 0 0 0 0 0]
# steps affected by the impulse: 8
# receptive field: 8
# first affected step: 2 (never before 2: no future leak)
```

The impulse at t = 2 changes outputs from t = 2 to t = 9, that is 8 steps. This is exactly the receptive field `1 + 1·(1+2+4) = 8`. Nothing before t = 2 changes, so the layer is causal.

```notebook
# Run with PyTorch. A causal dilated conv layer = pad on the left, then Conv1d.
import torch
import torch.nn as nn
import torch.nn.functional as F

class CausalConv1d(nn.Module):
    def __init__(self, c_in, c_out, kernel_size, dilation):
        super().__init__()
        self.pad = (kernel_size - 1) * dilation          # how much past we need
        self.conv = nn.Conv1d(c_in, c_out, kernel_size, dilation=dilation)

    def forward(self, x):                                # x: [batch, channels, time]
        return self.conv(F.pad(x, (self.pad, 0)))        # pad only on the LEFT
```

Note: PyTorch `Conv1d` wants `[batch, channels, time]`, so you transpose the `[batch, time, features]` tensor first.

## Common mistakes

- Using symmetric padding (`padding="same"`) in a library and leaking the future.
- Receptive field much smaller than the input window, or much larger (wasted compute).
- Forgetting that the axes of `Conv1d` are `[batch, channels, time]`.
- Using too few layers and assuming the model "sees" the yearly season.
- Dropout left on during evaluation.

## Interview lens

**Typical question:** "What is a dilated causal convolution and why use it for forecasting?"

**Strong answer:** A causal convolution only uses the current and past values, so there is no leakage from the future. Dilation makes the kernel skip steps, so the receptive field grows exponentially with depth. With kernel size k and dilations 1, 2, 4, ..., the receptive field is 1 + (k − 1) · (sum of dilations). Compared with an LSTM, a TCN trains in parallel and has a known memory length. I would set the receptive field to cover at least one full season of my data.

**Red flags:** cannot say why left padding is needed; thinks dilation adds parameters; mixes up the receptive field and the number of layers.

## Real world

- WaveNet (van den Oord et al., DeepMind, 2016) used dilated causal convolutions to generate raw audio.
- The TCN paper (Bai, Kolter and Koltun, 2018) made this design a general recipe for sequences.
- Dilated causal convolutions are also used inside forecasting models in libraries such as GluonTS and Darts.

## Key points

- A causal convolution pads on the left and uses only the present and past.
- Dilation skips steps. With dilations 1, 2, 4, ... the receptive field doubles per layer.
- `RF = 1 + (k − 1)·(sum of dilations)`.
- TCNs train in parallel and have a known, fixed memory; residual connections make deep stacks trainable.
