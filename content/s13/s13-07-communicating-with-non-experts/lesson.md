---
id: s13-07-communicating-with-non-experts
title: Explaining forecasts to non-experts
minutes: 25
level: intermediate
goals: [Explain a forecast in three sentences a manager can act on, Show uncertainty with a range and not with jargon, Answer why the forecast is wrong without being defensive, Pick one chart and one number for a slide]
prereqs: [s13-01-how-interviews-work]
tags: [communication, stakeholders, uncertainty, storytelling]
skills: [communication, uncertainty]
---

## Warm-up

```check
{"q": "A 90% prediction interval for next week's sales is 800 to 1,200. What does it mean in plain words?", "type": "single",
 "options": ["Sales will be exactly 1,000", "About 9 weeks out of 10 we expect sales between 800 and 1,200", "The model is 90% accurate", "Sales cannot be below 800"],
 "answer": 1,
 "why": ["A range is not one number.", "Correct: it describes how often the real value should fall inside the range.", "Accuracy is a different idea.", "Values can fall outside the range, about 1 time in 10."]}
```

## Why it matters

In your first week at a company, a manager will ask: "Can I trust this number?" You will not have a minute to explain ARIMA. If you can answer in three clear sentences, you earn trust. Interviewers test this on purpose. They say: "Explain this to a store manager." Strong candidates drop jargon, give a number, give a range, and say what to do.

## The 3-sentence forecast

Use this order for any forecast you present:

1. **The number and the range.** "We expect about 1,000 units next week, most likely between 800 and 1,200."
2. **The reason.** "This is higher than last week because of the holiday and the promotion."
3. **The action and the risk.** "Order 1,150 to be safe on stock-outs. The main risk is bad weather."

Notice: no model names, no formulas, one action.

```chart
{"title": "One chart for a manager: history, forecast and a range", "x": "week", "height": 240,
 "series": [
   {"name": "history", "x": [1,2,3,4,5,6,7,8], "y": [920, 950, 900, 980, 1010, 960, 990, 1000]},
   {"name": "forecast", "x": [8,9,10,11], "y": [1000, 1020, 1030, 1050], "dash": true},
   {"name": "upper (high case)", "x": [8,9,10,11], "y": [1000, 1180, 1230, 1280], "dash": true},
   {"name": "lower (low case)", "x": [8,9,10,11], "y": [1000, 860, 830, 820], "dash": true}
 ],
 "marks": [{"x": 8, "label": "today"}],
 "caption": "The range grows with the distance from today. One chart, one message: plan for the middle, prepare for the edges."}
```

```check
{"q": "Which is the best opening sentence for a store manager?", "type": "single",
 "options": ["Our LightGBM model with quantile loss achieved a pinball loss of 12.4.", "We expect about 1,000 units next week, most likely between 800 and 1,200.", "The residuals are not normally distributed.", "The MASE is 0.82."],
 "answer": 1,
 "why": ["Jargon, no decision.", "Correct: a number and a range in plain words.", "A technical remark, not helpful for the decision.", "A metric the manager does not know."]}
```

## Say uncertainty with words and ranges

People understand **ranges** and **scenarios**. They do not understand "standard error".

- Say "between 800 and 1,200", not "plus or minus 200 at a 90% level".
- Give two or three scenarios: low, expected, high. Say what causes each.
- Use frequencies: "about 1 week in 10 sales fall outside this range".
- Say what you do not know: "We do not know the effect of the new competitor yet."

Avoid false precision. "1,003.7 units" is not honest if the range is 800 to 1,200.

```check
{"q": "Which statement shows uncertainty well?", "type": "single",
 "options": ["Sales will be 1,003.7 units.", "Sales will be about 1,000 units, between 800 and 1,200 in 9 weeks out of 10.", "Sales are unpredictable.", "There is a 90% confidence level."],
 "answer": 1,
 "why": ["False precision.", "Correct: rounded number, a range, and a frequency.", "True but gives no help.", "Uses jargon without the range."]}
```

## When the forecast is wrong

It will happen. A calm answer has four parts.

1. **Say the facts.** "We forecast 1,000 and sales were 1,350."
2. **Say the cause, if you know it.** "A promotion started that was not in our data."
3. **Say if it was inside the range.** If yes: "This was in the high case." If no: "This is outside the range, so we treat it as an error to fix."
4. **Say the fix.** "We now read the promotion calendar every morning."

Do not blame the data or the user. Do not hide the miss.

```check
{"q": "A forecast missed by 35%. Which first sentence is best?", "type": "single",
 "options": ["The data was bad.", "You gave us the wrong promotion dates.", "We forecast 1,000 and sales were 1,350. Here is what we found and the fix.", "Forecasts can never be right."],
 "answer": 2,
 "why": ["Blaming data sounds defensive.", "Blaming a person damages trust.", "Correct: facts first, then cause and fix.", "True in theory, but it avoids ownership."]}
```

## Pick one number and one chart

For a slide, choose:

- **One headline number** tied to the decision (units, money, hours of staff).
- **One chart** with the forecast and its range.
- **One action.**

Put the lift in business terms when you can: "Forecast error fell from 14% to 10%. This is about 30 fewer stock-outs per week."

## Worked example

A function turns three numbers into a plain-English message. This is how you can prepare a daily report text.

```python
def explain(point, low, high, last_week, reason):
    change = (point - last_week) / last_week * 100
    direction = "higher" if change > 0 else "lower"
    return (f"We expect about {round(point, -1):,.0f} units, most likely between "
            f"{round(low, -1):,.0f} and {round(high, -1):,.0f}. "
            f"That is {abs(change):.0f}% {direction} than last week because {reason}.")

print(explain(1034, 812, 1189, 940, "of the holiday and the promotion"))
# Output:
# We expect about 1,030 units, most likely between 810 and 1,190. That is 10% higher than last week because of the holiday and the promotion.
```

Check the message: round numbers, a range, a clear reason. A manager can read this in 10 seconds.

## Common mistakes

- Starting with the model instead of the decision.
- Showing a table of metrics with no meaning.
- Using words like "stationary", "residual", "heteroscedastic".
- One number with no range.
- Defending the model when it is wrong.
- Too many charts on one slide.

## Interview lens

**Typical question:** "Explain to a non-technical VP why the forecast was 25% too low last week."

**Strong answer:** "Last week we forecast 800 and sales were 1,000. A large customer started a promotion that was not in our data, so the model did not know. That day was outside our usual range, so I count it as a miss, not bad luck. We fixed it by reading the promotion calendar every day and adding an alert when sales are far above forecast. From now on you will see a high case that includes known promotions."

**Red flags:** blames others; uses jargon; no fix; no number.

## Real world

- Weather services show forecasts with probabilities ("40% chance of rain"). Many studies of risk communication say people use probability statements better than technical terms. This is a common reason why probabilistic forecasts are shown as ranges or fans in public charts.
- Many central banks publish fan charts for inflation and growth, which show the range of likely outcomes around a central forecast.

## Key points

- Use the 3-sentence forecast: number and range, reason, action and risk.
- Show uncertainty as a range or scenarios, in plain words.
- When wrong: facts, cause, inside the range or not, fix. Never blame.
- One slide: one number, one chart, one action.
