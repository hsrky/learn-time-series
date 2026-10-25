---
id: s13-02-concept-question-bank
title: Concept question bank (timed)
minutes: 40
level: intermediate
goals: [Answer short concept questions in four sentences or less, Recognise the 12 questions that appear again and again, Practise under a timer with a 22-question bank]
prereqs: [s13-01-how-interviews-work]
tags: [interview, concepts, question-bank]
skills: [baseline-first, leakage, backtest, metrics, uncertainty]
---

## Warm-up

```check
{"q": "In which round do you hear short 'why' questions such as 'why not a random split?'", "type": "single",
 "options": ["Recruiter screen", "ML fundamentals", "Behavioural", "Salary talk"],
 "answer": 1,
 "why": ["The recruiter call is about your story and logistics.", "Correct: fundamentals rounds use short, exact concept questions.", "Behavioural rounds ask about past work with people.", "Salary talk is not a technical round."]}
```

```check
{"q": "Which metric compares your error with the error of a naive forecast and does not depend on the unit?", "type": "single", "options": ["RMSE", "MASE", "Raw error in dollars", "R-squared"], "answer": 1, "why": ["RMSE has the unit of the data.", "Correct: MASE divides by the naive error, so it is scale-free.", "A dollar error depends on the unit.", "R-squared is not a standard forecast metric."]}
```

## Why it matters

Concept questions are fast. The interviewer asks 10 to 15 of them in one hour. Each answer should take 30 to 60 seconds. If you ramble, you lose time and trust. If you know the **shape** of an answer, you stay calm. This lesson gives you that shape. The quiz below has 22 questions from all topics. The flashcards hold the facts you need.

## The four-step answer shape

Use this pattern for any "what is X" or "why X" question:

1. **Say it in one sentence.** The plain definition.
2. **Say why it matters.** The risk it removes.
3. **Give a tiny example with numbers.**
4. **Add one trade-off or limit.**

Example. Question: "What is [[data leakage]]?"

1. Leakage is when the model sees information at training time that it will not have at prediction time.
2. It makes offline scores too good, and the model fails in production.
3. Example: a rolling mean that includes today's sales, when you predict today's sales.
4. The fix is to build every feature from data older than the forecast time. A random split can also cause it.

```check
{"q": "What is the best first step in a short concept answer?", "type": "single",
 "options": ["A long history of the method", "A one-sentence plain definition", "A formula with all symbols", "A list of five libraries"],
 "answer": 1,
 "why": ["History uses your time and shows nothing about understanding.", "Correct: a short, clear definition shows you understand and gives the interviewer a base to ask more.", "Formulas can come later, if asked.", "Libraries are not the concept."]}
```

## The 12 questions that come back

These appear in many loops. Know a short answer for each.

| Question | Core of the answer |
|---|---|
| Why a baseline first? | It sets the bar. Seasonal naive often wins. Report lift over it. |
| Why not a random split? | It lets the model see the future. Split by time. |
| What is stationarity? | Mean, spread and autocorrelation do not change with time. |
| How do you pick ARIMA orders? | Difference until stationary, read ACF and PACF, compare AIC on a hold-out. |
| MAPE problems? | Explodes near zero, undefined at zero, biased to under-forecast. |
| What is MASE? | Error scaled by the in-sample naive error. Below 1 beats naive. |
| Global vs local models? | Global shares strength across series. Local fits each one alone. |
| Recursive vs direct? | Recursive feeds its own forecasts back. Direct trains one model per step. |
| How do you do a backtest? | Several forecast origins, train on the past only, score each horizon. |
| Point vs probabilistic forecast? | Point gives one number. Probabilistic gives quantiles or a distribution. |
| How do you detect drift? | Compare recent inputs and errors with a reference window. |
| When not to use deep learning? | Few series, short history, strong seasonal naive, strict latency. |

```widget
{"name": "quantile-loss", "params": {"q": 0.9}}
```

```check
{"q": "Seasonal naive MAE is 10 and your model's MAE is 9.5 on a good backtest. What do you say?", "type": "single",
 "options": ["The model is clearly better; ship it", "The lift is 5%, small; check cost, risk, and error by segment before deciding", "Seasonal naive is always wrong", "MAE cannot compare models"],
 "answer": 1,
 "why": ["A 5% lift may not pay for the extra complexity.", "Correct: report the lift and weigh it against cost and risk.", "Seasonal naive is a strong, honest baseline.", "MAE can compare two models on the same data."]}
```

## Compare with numbers, not adjectives

Strong answers include one number. "MAPE blows up near zero" is good. "A day with actual 1 and forecast 10 gives 900% error, which can dominate the average" is better. The worked example shows this.

## Worked example

Four days of sales. On three days the shop sells about 100 units. On one slow day it sells 1 unit. See how MAPE and WAPE react.

```python
import numpy as np

actual = np.array([100.0, 100.0, 100.0, 1.0])
fcst   = np.array([ 90.0, 110.0, 100.0, 10.0])

ape = np.abs(actual - fcst) / actual            # error per day, as a share of actual
mape = ape.mean()                               # simple average of shares
wape = np.abs(actual - fcst).sum() / actual.sum()  # total error / total actual

print("per-day APE:", np.round(ape, 2))
print(f"MAPE = {mape:.1%}")
print(f"WAPE = {wape:.1%}")
# Output:
# per-day APE: [0.1 0.1 0.  9. ]
# MAPE = 230.0%
# WAPE = 9.6%
```

One slow day (actual 1) makes MAPE look terrible. WAPE weights days by volume, so the big days decide. That is the reason many retail teams prefer WAPE.

## Common mistakes

- Answering with a list of names (ARIMA, ETS, LSTM) and no reason.
- Saying "it depends" and then stopping. Say what it depends on.
- Mixing up bias (always too high or too low) and variance (error that changes a lot).
- Using one metric for every goal.
- Saying "accuracy" for a regression forecast.

## Interview lens

**Typical question:** "Your MAPE is 40% but the business says the forecast is fine. Why?"

**Strong answer:** "MAPE is dominated by small-volume days or items, where small absolute errors are large percentages. The business cares about big volumes. I would check WAPE, which weights by volume, and look at error by segment. I would also check bias, because MAPE hides if we are always low. Then I would agree one main metric with the business."

**Red flags:** treating MAPE as the one true metric; no mention of zero or small actuals; no mention of bias.

## Real world

- The M4 forecasting competition (2018) used sMAPE and MASE and showed that simple methods and combinations are hard to beat. Its report is public.
- The M5 competition (2020, Walmart data) used a weighted scaled error, WRMSSE, for a sales hierarchy. LightGBM-based solutions won.

## Key points

- Answer in four steps: one-line definition, why it matters, a tiny example, one trade-off.
- Know the 12 recurring questions by heart.
- Put one number in every answer.
- Use the 22-question quiz and the flashcards under a timer: 90 seconds per question.
