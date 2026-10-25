---
id: s6-10-state-space-models
title: State-space models for long sequences (S4 and Mamba)
minutes: 30
level: advanced
goals: [Explain a linear state-space model as a recurrence and as a convolution, Describe in simple words what S4 and Mamba add, Judge when a long-sequence model is worth the cost]
prereqs: [s6-02-rnn-lstm-gru, s6-03-tcn-causal-convolutions]
tags: [ssm, s4, mamba, long-sequences]
skills: [scale, from-scratch]
---
## Warm-up

```check
{"q": "Which model type cannot train in parallel over time because step t needs step t−1?", "type": "single",
 "options": ["RNN", "Causal convolution (TCN)", "Linear model on a window"], "answer": 0,
 "why": ["Correct.", "Convolutions run on all positions at once.", "A linear model works on the full window at once."]}
```

```check
{"q": "Attention cost grows with the number of tokens n like:", "type": "single",
 "options": ["n", "n log n", "n squared"], "answer": 2,
 "why": ["That would be linear.", "That is a cheaper approximation (Informer).", "Correct for full self-attention."]}
```

## Why it matters

Some tasks have very long sequences: sensor data at 1000 Hz, minute data for a year (500,000 steps), audio, ECG. Attention at that length is too expensive (n squared). RNNs are cheap but forget and train slowly.
**[[state-space model|State-space models]] (SSMs)** aim for both: cost that grows linearly with length, long memory, and parallel training. S4 (2021) and Mamba (2023) are the best-known ones.
**2026 trend:** Mamba-style blocks appear in many new sequence models. In time series, results versus simple baselines are mixed, so the interview answer is about trade-offs, not hype.

## A state-space model in one line

A (discrete, linear) state-space model keeps a hidden **state** vector `h` and reads one input value `u` at a time:

`h(t) = A · h(t−1) + B · u(t)`
`y(t) = C · h(t)`

- `h(t)`: the state, a vector with N numbers (the memory).
- `u(t)`: the input at time t. `y(t)`: the output.
- `A`: how the state evolves by itself (decay and mixing). `B`: how the input enters the state. `C`: how the state is read out.

Compare with an RNN: it is the same loop, but **without the non-linear tanh**. Because it is linear, we can do clever things with the math.

Example with one number of state: `A = 0.9`, `B = 1`, `C = 1`. The input is a single pulse `1, 0, 0, 0, ...`. The state is `1, 0.9, 0.81, 0.729, ...`. The memory of the pulse fades slowly: this is a **long memory** if `A` is close to 1.

```check
{"q": "A = 0.5, B = 1, C = 1, pulse input 1, 0, 0, 0. What is the output at t = 3?", "type": "numeric", "answer": 0.125, "tol": 0.0001,
 "why": "y(0) = 1, y(1) = 0.5, y(2) = 0.25, y(3) = 0.125. The state is halved at each step."}
```

## Two views: loop or convolution

Unroll the loop. The output is a weighted sum of all past inputs:

`y(t) = sum over k of  K(k) · u(t − k)`, with `K(k) = C · Aᵏ · B`

This is a **convolution** with a kernel `K` as long as the sequence. So an SSM has two equal forms:

| View | Use | Cost |
|---|---|---|
| Recurrence (the loop) | inference: one step at a time, constant memory | O(1) per new step |
| Convolution | training: all positions in parallel (with FFT) | about O(n log n) |

This is the key idea of S4: train like a CNN, run like an RNN.

```chart
{"title": "Kernel K(k) of a state-space model: memory fades with the lag k", "x": "lag k", "height": 200,
 "series": [
   {"name": "A = 0.9 (long memory)", "gen": [["exp", {"start": 1, "rate": -0.105}]], "n": 40},
   {"name": "A = 0.5 (short memory)", "gen": [["exp", {"start": 1, "rate": -0.693}]], "n": 40, "dash": true}
 ],
 "caption": "The kernel is the weight of an input k steps ago. A larger A keeps the past alive longer."}
```

## S4: make long memory trainable

Gu, Goel and Ré (ICLR 2022) introduced **S4**, the *Structured State Space sequence* model. Two problems had to be solved:

1. **Good memory.** A random `A` forgets or explodes. S4 starts `A` from a special structured matrix (HiPPO) designed to remember the history of the input well, and parameterizes it so the kernel can be computed fast.
2. **Speed.** Computing the kernel for a long sequence must be cheap. S4 uses a structure that makes it fast and numerically stable.

S4 reported strong results on the Long Range Arena benchmark, which tests sequences of thousands of steps, where plain Transformers struggled.

## Mamba: let the model choose what to remember

A fixed `A, B, C` treats every input the same. But often you want to **ignore** noise and **remember** an important event. Mamba (Gu and Dao, December 2023) makes `B`, `C` and the step size depend on the **current input**. This is a *selective* state-space model.

- Selection = a gate: "write this input into memory, or skip it".
- A selective model is no longer a fixed convolution. Mamba computes it with a fast, hardware-aware **scan** on the GPU instead.
- Cost grows **linearly** with the sequence length.

For time series, several papers have used Mamba blocks as the backbone of a forecaster. The ideas are promising for very long inputs and many variables. Results against a good linear model, PatchTST or boosted trees have been mixed, and the field moves quickly. Treat any ranking as a snapshot.

```check
{"q": "What is the main change from S4 to Mamba?", "type": "single",
 "options": ["The parameters B, C and step size depend on the input (selection).", "It uses attention instead of a state.", "It removes the state."], "answer": 0,
 "why": ["Correct.", "Mamba has no attention in its core block.", "The state is still there."]}
```

## Worked example

We verify that the loop view and the convolution view give the same output. Then we count the cost of attention vs a state-space scan for a long series.

```python
import numpy as np

# a small linear SSM with state size N = 2
A = np.diag([0.9, 0.5])          # state transition (diagonal for simplicity)
B = np.array([1.0, 1.0])
C = np.array([1.0, 1.0])

rng = np.random.default_rng(0)
u = rng.normal(size=12)          # input sequence

# view 1: the recurrence (loop)
h = np.zeros(2)
y_loop = []
for ut in u:
    h = A @ h + B * ut
    y_loop.append(C @ h)
y_loop = np.array(y_loop)

# view 2: the convolution with kernel K(k) = C A^k B
n = len(u)
K = np.array([C @ np.linalg.matrix_power(A, k) @ B for k in range(n)])
y_conv = np.array([sum(K[k] * u[t - k] for k in range(t + 1)) for t in range(n)])

print("same output:", np.allclose(y_loop, y_conv))
print("kernel first 4:", K[:4].round(3))

# cost comparison for a series with 100,000 steps
n_long = 100_000
print("attention score table entries:", f"{n_long ** 2:,}")
print("one scan over the sequence, steps:", f"{n_long:,}")

# Output:
# same output: True
# kernel first 4: [2.    1.4   1.06  0.854]
# attention score table entries: 10,000,000,000
# one scan over the sequence, steps: 100,000
```

Both views agree. For 100,000 steps, full attention would need 10 billion scores per head and layer, while a scan needs one pass of 100,000 steps.

```notebook
# Mamba in PyTorch needs a GPU and the mamba-ssm package; check its README for the current API and install steps.
# A minimal usage pattern (names may differ by version):
import torch
from mamba_ssm import Mamba

block = Mamba(d_model=64, d_state=16, d_conv=4, expand=2).to("cuda")
x = torch.randn(8, 1024, 64, device="cuda")   # [batch, time, channels]
y = block(x)                                  # same shape as x
```

## Common mistakes

- Using a long-sequence model on short series (100 to 500 steps), where a linear model or boosted trees are cheaper and as good.
- Believing "linear time" means "fast in practice". Real speed depends on the implementation and hardware.
- Comparing to weak baselines only.
- Forgetting that SSMs, like RNNs, can still lose old information if `A` is not well set.
- Treating one benchmark as proof for your data.

## Interview lens

**Typical question:** "What is a state-space model like S4 or Mamba, and why would you use it for long sequences?"

**Strong answer:** A linear state-space model keeps a hidden state updated by `h = A·h + B·u` and reads out `y = C·h`. Because it is linear, it can be run as a recurrence at inference time with constant cost per step, and as a long convolution during training so it parallelizes. S4 adds a special initialization of `A` for long memory and a fast way to compute the kernel. Mamba makes the parameters depend on the input, so the model can choose what to remember, and runs with a scan, giving linear cost in length. For forecasting I would use it only for very long inputs or high-frequency data, and compare it with a linear model, PatchTST and boosted trees first.

**Red flags:** saying SSMs are just LSTMs; claiming Mamba always beats Transformers; not mentioning the two views (recurrence and convolution).

## Real world

- S4 (Gu, Goel, Ré; Stanford; ICLR 2022) and Mamba (Gu and Dao; December 2023) were developed for general sequence tasks such as language, audio and genomics.
- Time series papers have adapted Mamba to forecasting. Names and results change quickly, so check recent benchmarks and reproduce them before you trust them.

## Staff lens

- **Adopting a new architecture.** Use a checklist: does it beat the baseline ladder on our data, after cost? Is there maintained library support? Can on-call engineers debug it? A paper result alone is not enough.
- **Timeboxing.** Give research a fixed budget (for example two weeks and a shared backtest). If the new model does not win, stop and write down the result.
- **Evaluation governance.** Keep the benchmark private to the team and refresh it, so models are not tuned to a public leaderboard.

## Key points

- A linear state-space model: `h = A·h + B·u`, `y = C·h`. It works as a loop (inference) or as a convolution (training).
- S4 makes long memory trainable with a special `A` and a fast kernel. Mamba makes parameters depend on the input (selection).
- Cost grows linearly with length, unlike full attention (n squared).
- For time series, results against simple baselines are mixed: test before you adopt.
