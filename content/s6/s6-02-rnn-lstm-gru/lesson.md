---
id: s6-02-rnn-lstm-gru
title: RNN, LSTM and GRU
minutes: 25
level: intermediate
goals: [Explain the hidden state of a recurrent network, Describe the LSTM and GRU gates in simple words, Compute one RNN step by hand and in numpy]
prereqs: [s6-01-windowed-datasets]
tags: [rnn, lstm, gru, deep-learning]
skills: [from-scratch]
---
## Warm-up

```check
{"q": "A window has shape [32, 96, 3]. How many time steps does one example have?", "type": "numeric", "answer": 96, "tol": 0,
 "why": "The shape is [batch, time, features], so time = 96."}
```

```check
{"q": "Where do you compute the mean and std used for scaling?", "type": "single",
 "options": ["On the full dataset", "On the training part only", "On the validation part only"], "answer": 1,
 "why": ["That leaks future information.", "Correct: scale statistics come from the past only.", "Validation must not set the scale."]}
```

## Why it matters

Before 2017, recurrent networks were the default deep model for sequences. They are still used for small and medium forecasting tasks, in production systems, and in many interview questions.
DeepAR (a later lesson in this stage) is built on an LSTM. If you understand the cell, you understand how a network can "remember" something from many steps ago. You also see why it sometimes forgets.

## The recurrent idea: a hidden state

A [[recurrent neural network]] (RNN) reads a sequence **one step at a time**. It keeps a vector called the [[hidden state]], which is its memory.
At each step it mixes the new input with the old memory to produce new memory.

Small example with one input and one memory number. Weights: input weight 0.5, memory weight 0.9, bias 0.

- Step 1: input 1, old memory 0. New memory = tanh(1·0.5 + 0·0.9) = tanh(0.5) = 0.462.
- Step 2: input 1, old memory 0.462. New memory = tanh(0.5 + 0.462·0.9) = tanh(0.916) = 0.724.

The memory grew because the same input came twice.

## The RNN formula

Here is the same step as a formula:

`h(t) = tanh( x(t)·Wxh + h(t−1)·Whh + b )`

- `x(t)`: the input at step t (a vector with F numbers).
- `h(t−1)`: the memory from the last step (H numbers).
- `Wxh`, `Whh`, `b`: weights the network learns. The same weights are used at every step.
- `tanh`: a function that squashes any number into the range −1 to 1.

```check
{"q": "Why can an RNN not process all its time steps at the same time?", "type": "single",
 "options": ["It has too many weights.", "Step t needs the hidden state from step t−1.", "tanh is slow."],
 "answer": 1,
 "why": ["The weight count is not the reason.", "Correct: the steps depend on each other, so they run in order.", "tanh is cheap."]}
```

## The problem: forgetting

To train an RNN, the error signal travels backwards through all steps. At each step it is multiplied by a number related to `Whh`.
If this number is smaller than 1, the signal shrinks step after step. After 50 steps it is almost 0. This is the [[vanishing gradient]].
The network cannot learn that something 50 steps ago matters. (If the number is bigger than 1, the signal explodes. People limit this with *gradient clipping*.)

```chart
{"title": "A signal multiplied by 0.9 each step vanishes", "x": "steps back", "height": 200,
 "series": [{"name": "signal strength", "gen": [["exp", {"start": 1, "rate": -0.105}]], "n": 50}],
 "caption": "After about 22 steps, the signal is already below 10% of its start. A plain RNN has trouble with long memory."}
```

## LSTM: memory with gates

The [[LSTM]] (Hochreiter and Schmidhuber, 1997) adds a second memory line, the [[cell state]] `c`. A [[gate]] is a number between 0 and 1 for each memory slot. It works like a tap: 0 = closed, 1 = open.

| Gate | Question it answers | Effect |
|---|---|---|
| **Forget** gate `f` | "How much of the old memory do I keep?" | `c` is multiplied by `f` |
| **Input** gate `i` | "How much of the new idea do I write?" | new idea times `i` is added to `c` |
| **Output** gate `o` | "How much of the memory do I show?" | `h = o · tanh(c)` |

Core update: `c(t) = f·c(t−1) + i·g`, where `g` is the new idea, `g = tanh(x·Wg + h·Ug + b)`.
Because the old memory is *added to*, not squashed again, the signal can travel many steps with little loss. If `f` is close to 1, the memory stays.

```check
{"q": "An LSTM forget gate has value 0 for a memory slot. What happens to that slot?", "type": "single",
 "options": ["It is kept unchanged.", "It is erased.", "It is doubled."],
 "answer": 1,
 "why": ["That would be a forget gate of 1.", "Correct: c is multiplied by 0.", "Gates are between 0 and 1, so they never double."]}
```

## GRU: a lighter cousin

The [[GRU]] (Cho et al., 2014) merges the two memories into one and uses two gates:

- **Update gate** `z`: how much to replace the old memory with a new candidate.
- **Reset gate** `r`: how much of the old memory to use when building the candidate.

A GRU has about 25% fewer parameters than an LSTM of the same size (3 weight blocks instead of 4). It often reaches a similar accuracy and trains faster.
Simple guide for forecasting: try GRU first for speed, LSTM if you need a bit more capacity. Check both against a simple baseline.

Parameter count per layer (F inputs, H hidden): LSTM `4·(F·H + H·H + H)`, GRU `3·(F·H + H·H + H)`.

```check
{"q": "F = 1 input, H = 32 hidden units. How many parameters in one LSTM layer (4·(F·H + H·H + H))?", "type": "numeric", "answer": 4352, "tol": 0,
 "why": "F·H = 32, H·H = 1024, H = 32. The sum is 1088. Times 4 is 4352."}
```

## From cell to forecast

For forecasting, you run the cell over the input window `[time, features]`. Then you take the last hidden state and put it through a small linear layer that outputs the `horizon` values. This is the "many-to-one" design.
The alternative is to run the cell also on the future steps and feed back its own predictions (autoregressive). The next lessons show it.

```notebook
# Run on your laptop or a Kaggle notebook (needs PyTorch)
import torch
import torch.nn as nn

class LSTMForecaster(nn.Module):
    def __init__(self, n_features, hidden, horizon):
        super().__init__()
        self.lstm = nn.LSTM(n_features, hidden, batch_first=True)  # input: [batch, time, features]
        self.head = nn.Linear(hidden, horizon)

    def forward(self, x):
        out, (h, c) = self.lstm(x)        # out: [batch, time, hidden]
        return self.head(out[:, -1])      # last step -> [batch, horizon]

model = LSTMForecaster(n_features=3, hidden=64, horizon=24)
print(model(torch.randn(32, 96, 3)).shape)   # torch.Size([32, 24])
```

## Worked example

We compute the RNN steps from the example above, then one LSTM step with small random weights.

```python
import numpy as np

def sigmoid(z):
    return 1 / (1 + np.exp(-z))

# --- RNN: the two steps from the text (1 input, 1 memory number)
Wxh, Whh, b = 0.5, 0.9, 0.0
h = 0.0
for step, x in enumerate([1.0, 1.0], start=1):
    h = np.tanh(x * Wxh + h * Whh + b)
    print("RNN step", step, "h =", round(h, 3))

# --- LSTM: one step with F=2 inputs and H=3 memory slots
rng = np.random.default_rng(0)
F, H = 2, 3
W = rng.normal(0, 0.5, size=(F, 4 * H))    # input weights for the 4 blocks: f, i, o, g
U = rng.normal(0, 0.5, size=(H, 4 * H))    # memory weights for the 4 blocks
b = np.zeros(4 * H)
b[:H] = 1.0                                 # common trick: start with forget gate bias 1 (keep memory)

x = np.array([1.0, -0.5])
h_prev = np.zeros(H)
c_prev = np.array([0.5, -0.5, 1.0])

z = x @ W + h_prev @ U + b
f, i, o = sigmoid(z[:H]), sigmoid(z[H:2*H]), sigmoid(z[2*H:3*H])   # gates in (0, 1)
g = np.tanh(z[3*H:])                                                  # new idea in (-1, 1)
c = f * c_prev + i * g                                                # forget some, write some
h = o * np.tanh(c)                                                    # show part of the memory
print("forget gate", f.round(2))
print("new cell state", c.round(2))
print("new hidden state", h.round(2))
print("parameters (F=1, H=32):", 4 * (1 * 32 + 32 * 32 + 32))

# Output:
# RNN step 1 h = 0.462
# RNN step 2 h = 0.724
# forget gate [0.84 0.73 0.84]
# new cell state [-0.   -0.43  0.8 ]
# new hidden state [-0.   -0.22  0.28]
# parameters (F=1, H=32): 4352
```

Look at the forget gate: values between 0.7 and 0.85 keep most of the old cell state. That is the effect of the bias trick.

## Common mistakes

- Using a very long input window (1000+ steps) with an LSTM and expecting it to remember everything. Gates help, but they do not remove all forgetting.
- Not scaling the input. RNNs with `tanh` saturate for big inputs.
- Forgetting `batch_first=True` and mixing the axes.
- Training an LSTM and not comparing with seasonal naive or a gradient boosting model.
- Predicting all `horizon` steps from only the last hidden state without checking if errors grow with the horizon.

## Interview lens

**Typical question:** "What problem do LSTMs solve, and how?"

**Strong answer:** A plain RNN multiplies the error signal by the same weights at each step. So the signal vanishes over long spans and the network forgets. An LSTM keeps a separate cell state and updates it by adding, controlled by three gates: forget, input and output. The gates are numbers between 0 and 1 that decide what to keep, write and show. A GRU merges the cell and hidden state and has two gates, so it has fewer parameters. For time series, I would still start with a seasonal naive and a boosted-tree baseline. I would use an LSTM or GRU when I have many series or complex inputs.

**Red flags:** "LSTM never forgets"; confusing hidden state with cell state; no mention of vanishing gradients; saying deep learning always beats classical methods.

## Real world

- The DeepAR model from Amazon (Salinas et al.) uses LSTM layers. It is available in the GluonTS library.
- The winner of the M4 forecasting competition (Slawek Smyl, Uber) used a hybrid of exponential smoothing and recurrent networks (ES-RNN).

## Key points

- An RNN keeps a hidden state. It applies the same cell at every step: `h(t) = tanh(x·Wxh + h·Whh + b)`.
- Plain RNNs forget over long spans because the training signal vanishes.
- LSTM gates (forget, input, output) control a cell state that can carry information over many steps. GRU does the same with two gates.
- Steps run in order, so RNNs are hard to parallelize over time.
