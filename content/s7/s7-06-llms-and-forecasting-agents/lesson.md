---
id: s7-06-llms-and-forecasting-agents
title: LLMs and forecasting agents
minutes: 30
level: advanced
goals: [Explain LLMTime (numbers as text) and Time-LLM (reprogramming), Describe a forecasting agent that picks tools and explains results, Name the limits and write guardrails]
prereqs: [s7-05-benchmarking-honestly]
tags: [llm, llmtime, time-llm, agents, 2026-trend]
skills: [communication, production, from-scratch]
---
## Warm-up

```check
{"q": "A long number like 1234 may be split by a text tokenizer into '12' and '34'. Why is this a problem for forecasting?", "type": "single",
 "options": ["Place values become unclear for the model.", "The number gets bigger.", "It speeds up the model."], "answer": 0,
 "why": ["Correct: the model sees pieces without a fixed meaning for each digit.", "The value does not change.", "It does not speed anything up."]}
```

```check
{"q": "What does a good forecast evaluation always include?", "type": "single",
 "options": ["A time-based split and a seasonal naive baseline", "A random split", "Only the training error"], "answer": 0,
 "why": ["Correct.", "Random splits leak.", "Training error says nothing about the future."]}
```

## Why it matters

**2026 trend.** Large language models (LLMs) are now part of many analytics tools. People ask two questions. "Can I give my sales table to an LLM and ask for a forecast?" Or: "Can an LLM agent run the workflow?"
The honest answer has two parts. Using an LLM as a **forecaster** is usually expensive and not better than specialized models. An LLM can also be an **assistant around** a forecasting system. It can choose tools, run backtests and write the report. This can save time if you control it with a strict harness.

## LLMTime: numbers as text

**LLMTime** (Gruver, Finzi, Qiu and Wilson, NeurIPS 2023) showed that a general-purpose LLM can continue a numeric series *as text*. It needs no training on time series.

The recipe:

1. **Scale** the values so they are small, for example in a range of 0 to 10. Fix a number of decimals.
2. Write each value **digit by digit with spaces** (`1 2 3`), so a tokenizer cannot glue digits into odd pieces. Separate time steps with a comma.
3. Give the text to the LLM as a prompt and let it continue. Sample several continuations.
4. **Decode** the text back to numbers and take the median and quantiles of the samples.

## An encoding example

Example: values `1.23` and `45.6` with 2 decimals and padding become `0 1 2 3 , 4 5 6 0`. You implement this encoder in [[problem:llmtime-digit-encoding]].

The authors reported that this zero-shot approach could be competitive with specialized models on some data sets. Later work found it is sensitive to the setup and costly.

```check
{"q": "Why does LLMTime separate digits with spaces?", "type": "single",
 "options": ["So the tokenizer makes one token per digit and place values stay clear.", "To make the text prettier.", "To hide the data."], "answer": 0,
 "why": ["Correct.", "Not the reason.", "Not the reason."]}
```

## Time-LLM: reprogramming

**Time-LLM** (Jin et al., ICLR 2024) keeps the LLM **frozen** and trains small parts around it. It cuts the series into patches. A trained layer *reprograms* each patch into the word embedding space of the LLM. It maps patches to combinations of text "prototype" embeddings. A text prompt describes the task and the data set. The LLM output goes through a small trained head that gives the forecast.

The idea: reuse the LLM's sequence skills while training only a few parameters.

## A reality check

A 2024 study tested LLM-based forecasters with ablations. Its title is "Are Language Models Actually Useful for Time Series Forecasting?" (Tan et al., NeurIPS 2024). It found that **replacing the LLM by a simple attention layer, or removing it, often did not make results worse**. The LLM added a lot of compute. The message: do not assume that the language model is the reason for good numbers. Test an ablation.

Specialized time series foundation models are trained on series. Chronos, TimesFM and Moirai are examples (lessons 2 and 3). They are much smaller than general LLMs. They are the usual choice when you want a pre-trained forecaster.

```check
{"q": "An LLM-based forecaster scores well. What ablation would you run before crediting the LLM?", "type": "single",
 "options": ["Replace the LLM by a small attention layer or remove it, and re-evaluate.", "Make the prompt longer.", "Run it on training data."], "answer": 0,
 "why": ["Correct.", "That does not test the claim.", "Training data do not test generalization."]}
```

## Forecasting agents

A **forecasting agent** is an LLM that uses **tools** in a loop. Typical tools: load data, plot, run a baseline, run a model, run a backtest, get a metric. The model can be statsforecast or a foundation model. The LLM reads results and chooses the next step. At the end it writes a summary in plain language.

Good uses:

- **Model selection assistant:** propose candidate models for a series type and run the backtest tool.
- **Data checks:** find gaps, outliers, wrong frequencies, and ask for confirmation.
- **Explanations for non-experts:** turn metrics and charts into a short text.
- **Code help:** generate pipelines that a human reviews.

The rule: **the LLM proposes, the harness decides.** Numbers in the final answer must come from tool output. The choice of model must come from a backtest against a baseline, not from the opinion of the LLM.

```check
{"q": "In a safe forecasting agent, who decides which model goes live?", "type": "single",
 "options": ["A backtest harness with fixed rules, which the LLM cannot change", "The LLM, based on its feeling", "The user's first guess"], "answer": 0,
 "why": ["Correct.", "LLMs can state wrong reasons with confidence.", "Not evidence."]}
```

## Limits and risks

```chart
{"title": "Tokens needed as text (4 digits per value, plus one comma between values)", "x": "series length", "height": 200,
 "series": [{"name": "tokens", "kind": "bar", "y": [499, 2499, 4999, 24999]}],
 "caption": "Series of 100, 500, 1,000 and 5,000 values. Cost and delay grow with the number of tokens."}
```

| Limit | Why it matters |
|---|---|
| **Digit tokenization** | Numbers are split in odd ways unless you format them; long series need many tokens |
| **Cost and latency** | A series of 1,000 values with 4 digits each needs thousands of tokens per call; large models are slow |
| **Context limits** | Long histories do not fit; you must shorten or summarize |
| **Hallucinated explanations** | The LLM can write a confident reason ("because of the holiday") that is not in the data |
| **Non-determinism** | The same prompt can give different numbers; you need many samples and seeds |
| **Prompt injection** | Text inside data (a column name, a comment) can contain instructions; never let data text control tools |
| **Weak calibration** | Intervals from sampling are often not calibrated; measure coverage |
| **Privacy** | Sending data to an external API may break policy |

```check
{"q": "An agent says 'sales rose because of the new ad campaign'. The data contain no campaign information. What is this?", "type": "single",
 "options": ["A hallucinated explanation", "A verified insight", "A forecast"], "answer": 0,
 "why": ["Correct: the claim has no support in the tools' output.", "No evidence supports it.", "It is a claim about a cause, not a forecast."]}
```

## Worked example

Part 1: we encode a series as LLMTime text and count how many tokens it needs. Part 2: we write the "LLM proposes, harness decides" rule. The LLM call is replaced by a fixed stand-in function, so the example runs without any service.

```python
import numpy as np

# ---- part 1: LLMTime-style text for a series
def llm_encode(values, decimals=2):
    ints = [int(round(v * 10 ** decimals)) for v in values]
    width = max(1, max(len(str(abs(n))) for n in ints))
    parts = []
    for n in ints:
        digits = " ".join(str(abs(n)).zfill(width))
        parts.append(("- " + digits) if n < 0 else digits)
    return " , ".join(parts)

rng = np.random.default_rng(0)
series = np.round(20 + 5 * np.sin(np.arange(168) * 2 * np.pi / 24) + rng.normal(0, 0.5, 168), 2)
text = llm_encode(series[:3])
print("first 3 values as text:", text)
full = llm_encode(series)
n_tokens = len(full.split())           # one token per digit and per comma (a simple estimate)
print("one week of hourly data:", len(series), "values ->", n_tokens, "tokens")

# ---- part 2: the LLM proposes, the harness decides
def seasonal_naive(ctx, h, m=24):
    return np.resize(ctx[-m:], h)

def last_value(ctx, h, m=24):
    return np.full(h, ctx[-1])

CANDIDATES = {"seasonal_naive": seasonal_naive, "last_value": last_value}

def llm_propose():                      # stand-in for an LLM call
    return "last_value"                 # the "LLM" suggests a weaker model

def mase(y, f, ctx, m=24):
    return np.abs(y - f).mean() / np.abs(ctx[m:] - ctx[:-m]).mean()

ctx, future = series[:-24], series[-24:]
name = llm_propose()
score = mase(future, CANDIDATES[name](ctx, 24), ctx)
base = mase(future, seasonal_naive(ctx, 24), ctx)
print(f"proposed '{name}': MASE {score:.2f}; baseline MASE {base:.2f}")
accepted = score < 0.95 * base          # fixed rule: must beat the baseline by 5%
print("accepted:", accepted, "-> use", name if accepted else "seasonal_naive (fallback)")

# Output:
# first 3 values as text: 2 0 0 6 , 2 1 2 3 , 2 2 8 2
# one week of hourly data: 168 values -> 839 tokens
# proposed 'last_value': MASE 6.29; baseline MASE 1.14
# accepted: False -> use seasonal_naive (fallback)
```

One week of hourly data (only 168 values) already needs about 840 tokens as text. The harness rejected the proposal, because it did not beat the baseline. The LLM never has the last word.

```notebook
# An agent loop sketch with plain Python; replace call_llm with your provider's SDK.
import json

TOOLS = {"run_backtest": run_backtest, "plot_series": plot_series}   # your own functions

def agent(question, call_llm, max_steps=6):
    messages = [{"role": "user", "content": question}]
    for _ in range(max_steps):
        reply = call_llm(messages, tools=list(TOOLS))        # the LLM returns text or a tool request
        if reply.get("tool"):
            result = TOOLS[reply["tool"]](**reply["args"])   # YOUR code runs the tool
            messages.append({"role": "tool", "content": json.dumps(result)})
        else:
            return reply["text"]                              # final answer; check numbers against tool outputs
    return "stopped: too many steps"
```

## Common mistakes

- Using a general LLM as the main forecaster for thousands of series. It is slow and costly compared with specialized models.
- Letting the LLM quote numbers that were not produced by a tool.
- No fallback when the LLM or the tool fails.
- Letting data text reach the prompt unfiltered (prompt injection).
- Judging an LLM forecaster without an ablation or a seasonal naive baseline.

## Interview lens

**Typical question:** "Would you use an LLM for forecasting? How would you build a forecasting agent?"

**Strong answer:** As a direct forecaster, I would not choose a general LLM for large-scale work. It is costly, and digit tokenization is awkward. Studies like Tan et al. show the LLM part often adds little compared with simple components. Specialized foundation models like Chronos or TimesFM are the better pre-trained option. I do see value in an agent around the forecasting system. It can run data checks, call tools for baselines and models, run backtests, and write the summary. The agent proposes, but a fixed harness decides by backtest against seasonal naive. All numbers come from tool outputs. I log every step. I add a fallback and protection against prompt injection.

**Red flags:** "ask the LLM for the forecast"; trusting explanations without evidence; no baseline or fallback; sending sensitive data to an external API.

## Real world

- LLMTime (NeurIPS 2023) and Time-LLM (ICLR 2024) are the best-known research examples of language models for time series.
- Tan et al. (NeurIPS 2024) tested these ideas with ablations and found the LLM component often not needed.
- Forecasting libraries and cloud tools increasingly include natural-language assistants for data checks and reports. Their forecasts still come from tested models.

## Staff lens

- **Guardrails as platform features.** Build the harness once. It has frozen evaluation rules, tool allow-lists, logging, cost limits, and human sign-off for model changes. Then agents are safe to try for every team.
- **Build vs buy.** An LLM assistant layer is cheap to prototype and hard to make reliable. Decide which steps need a human (approval of a model change) and which can be automatic (data-quality alerts).
- **Evaluation governance.** Evaluate the agent too. Track how often its choices match the backtest winner and how often tool output supports its explanations. Track its cost per run.

## Key points

- LLMTime writes digits as text so an LLM can continue a series. It is flexible but costly and sensitive to the setup.
- Time-LLM reprograms patches for a frozen LLM; studies show the LLM part often adds little.
- A forecasting agent should propose; a fixed backtest harness should decide; numbers must come from tools.
- Main risks: digit tokenization, cost, hallucinated explanations, prompt injection, weak calibration, privacy.
