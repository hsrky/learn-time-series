---
id: s13-08-behavioural-stories
title: Behavioural stories with metrics (STAR)
minutes: 25
level: intermediate
goals: [Write a STAR story with a number in the result, Build a bank of 6 stories that cover the usual questions, Turn forecast error into money or time saved, Avoid claims you cannot defend]
prereqs: [s13-01-how-interviews-work]
tags: [behavioural, STAR, impact, storytelling]
skills: [communication]
---

## Warm-up

```check
{"q": "In which round do you hear 'Tell me about a time when you disagreed with a teammate'?", "type": "single",
 "options": ["Coding / OA", "Behavioural", "Time-series technical round", "Recruiter screen only"],
 "answer": 1,
 "why": ["Coding rounds test code.", "Correct: past behaviour is the topic of this round.", "The time-series technical round tests technical knowledge.", "Recruiters may ask, but the full round is behavioural."]}
```

```check
{"q": "A hiring loop has a timed online test with pandas code. What is it called?", "type": "single", "options": ["An OA (online assessment)", "A behavioural round", "A recruiter screen", "A design review"], "answer": 0, "why": ["Correct: an OA tests code under a time limit.", "A behavioural round asks about past work with people.", "A recruiter screen is a short call.", "A design review is about system design."]}
```

## Why it matters

Companies hire people, not only code. In the behavioural round the interviewer asks: "Will this person work well with us when things are hard?"

Your past is the best proof. A story with a number is easy to remember and easy to trust. A story without a number sounds like a guess. Prepare 6 stories once, and you can answer 30 different questions.

## STAR: four parts

**STAR** helps you keep a story short (about 2 minutes).

| Part | What to say | Length |
|---|---|---|
| **S**ituation | Where, when, what was the problem? | 1–2 sentences |
| **T**ask | What was your part? What was the goal? | 1 sentence |
| **A**ction | What did **you** do? Steps, decisions, why | 4–6 sentences |
| **R**esult | The number, what changed, what you learned | 2 sentences |

Use "I" for your actions, "we" for the team's result. Interviewers want to know what **you** did.

```chart
{"title": "Share of a 2-minute STAR answer (bars: S, T, A, R)", "x": "part", "height": 200,
 "series": [
   {"name": "seconds", "kind": "bar", "x": [1,2,3,4], "y": [20, 10, 65, 25]}
 ],
 "caption": "Most of the time goes to Action (bar 3). Keep the Situation short."}
```

```check
{"q": "Which part of STAR should take the most time?", "type": "single",
 "options": ["Situation", "Task", "Action", "Result"],
 "answer": 2,
 "why": ["Keep the background short.", "The task is one sentence.", "Correct: the interviewer wants to hear what you did and why.", "The result needs a number, but is short."]}
```

## Put a number in the Result

"I improved the forecast" is weak. Compare two results:

- Weak: "The new model was better."
- Strong: "WAPE fell from 14% to 10% over 12 weeks of backtest. Stock-outs in the pilot stores fell by 18%."

Where do numbers come from?

- **Accuracy:** WAPE, bias, lift over the baseline.
- **Money:** waste, lost sales, inventory cost, cloud cost.
- **Time:** hours saved per week, run time of a job from 6 hours to 40 minutes.
- **Adoption:** number of teams or stores that use it.

If you do not know a number, say how you would measure it. Never invent one. Interviewers often ask "How did you measure this?"

```check
{"q": "Which result line is the strongest?", "type": "single",
 "options": ["The project went well.", "The model was more accurate.", "WAPE fell from 14% to 10% in a 12-week backtest, and the pilot stores had 18% fewer stock-outs.", "Everyone was happy."],
 "answer": 2,
 "why": ["No evidence.", "No size.", "Correct: a metric, a period, and a business effect.", "Not measurable."]}
```

## Turn error into money

A rough conversion is fine if you state your assumptions. Example: a retailer sells 1,000 units per day per store of a product that costs 2 euros to make. Over-forecasting by 5% adds waste. Suppose a better forecast cuts the average over-forecast from 5% to 3%. Then 2% of 1,000 units, or 20 units per day, are not wasted. That saves 40 euros per day per store. State the assumptions: price, share of the over-forecast that becomes waste, number of stores.

```check
{"q": "Over-forecast falls from 6% to 4% on 500 units per day. Each wasted unit costs 3. All over-forecast becomes waste. Daily saving?", "type": "numeric",
 "answer": 30, "tol": 0.01,
 "why": "2% of 500 = 10 units per day. 10 × 3 = 30 per day."}
```

## The six stories to prepare

Pick real projects. Write each in STAR form with one number.

1. **A project you led** (ownership, delivery).
2. **A conflict or disagreement** (how you listened and decided).
3. **A failure or mistake** (what you learned; show a fix).
4. **A time you influenced without authority** (persuaded a team with data).
5. **A hard technical trade-off** (simple model versus complex, speed versus accuracy).
6. **A time you explained something technical to a non-expert** (see [[lesson:s13-07-communicating-with-non-experts]]).

Many questions can reuse these: "biggest challenge", "tight deadline", "unclear requirements", "mentoring".

## Time-series flavours

Good forecasting stories include:

- finding **leakage** in a validation setup, and how it changed the result.
- choosing a **baseline** that beat a complex model.
- a **bad forecast** and how you ran the post-mortem.
- balancing **accuracy and latency** or cost.
- pushing to have a **monitor** before launch.

```check
{"q": "You failed: your model's offline score was great, but live error was high because of leakage. How do you tell this story?", "type": "single",
 "options": ["Hide it; pick a different story", "Tell it: what happened, the number, what you changed (time-based backtest, review checklist), and the lasting result", "Blame the data team", "Say it was not your fault"],
 "answer": 1,
 "why": ["Failure stories are expected and valued.", "Correct: honesty, a fix, and a lasting change show growth.", "Blame ends trust.", "Ownership is what is tested."]}
```

## Worked example

Write the impact line from raw numbers so your story is exact. This code checks the maths before you say it out loud.

```python
# Before and after, measured on the same 12-week backtest
wape_before, wape_after = 0.14, 0.10
stockouts_before, stockouts_after = 50, 41          # per week in pilot stores
waste_before, waste_after = 1200, 1000              # units per week in pilot stores

rel_gain = (wape_before - wape_after) / wape_before
so_drop = (stockouts_before - stockouts_after) / stockouts_before
waste_drop = (waste_before - waste_after) / waste_before

print(f"WAPE: {wape_before:.0%} -> {wape_after:.0%} ({rel_gain:.0%} lower in relative terms)")
print(f"Stock-outs: {stockouts_before} -> {stockouts_after} per week ({so_drop:.0%} fewer)")
print(f"Waste: {waste_before} -> {waste_after} units per week ({waste_drop:.0%} less)")
# Output:
# WAPE: 14% -> 10% (29% lower in relative terms)
# Stock-outs: 50 -> 41 per week (18% fewer)
# Waste: 1200 -> 1000 units per week (17% less)
```

Say it as: "We cut WAPE from 14% to 10%, which is 29% lower in relative terms. In the pilot, stock-outs fell by 18% and waste by 17%."

Always say percentage points or relative change, so the number is clear.

## Common mistakes

- "We did everything" with no "I".
- No number in the result.
- Inventing a number you cannot defend.
- Blaming others in a conflict story.
- A story that is too long (more than 3 minutes).
- A failure story with no learning.
- Telling the technical details too long and forgetting the person side.

## Interview lens

**Typical question:** "Tell me about a time you improved a forecasting system."

**Strong answer:** "Situation: our weekly demand forecast for 300 stores had a WAPE of 14% and managers ignored it. My task was to improve it in one quarter. I built a seasonal naive baseline and a 12-week backtest. I found that holidays caused most error. I added holiday and promotion features to a global LightGBM. I shared weekly error reports with the managers to build trust. WAPE fell to 10%, and pilot stores had 18% fewer stock-outs. The managers now use the forecast in their ordering tool."

**Red flags:** "we" for everything; no number; the story ends before the result; blaming.

## Real world

- Many large companies publish their interview approaches and say they look for ownership and impact. The STAR format is widely recommended in public career guides.
- Public engineering blogs from forecasting teams often describe a bad forecast incident and the new checks that followed. This pattern, problem then action then lasting change, is what a good failure story looks like.

## Key points

- Use STAR: short Situation and Task, detailed Action, measured Result.
- Put a number in every Result; never invent one; state your assumptions.
- Prepare six stories that cover leadership, conflict, failure, influence, trade-off, and explanation.
- Include time-series flavours: leakage found, baseline won, post-mortem, monitor added.
