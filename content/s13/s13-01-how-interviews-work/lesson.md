---
id: s13-01-how-interviews-work
title: How time-series interviews are built
minutes: 20
level: intermediate
goals: [Name the six typical rounds of a forecasting interview, Say what each round tests, Build a weekly prep plan from your weak rounds]
prereqs: []
tags: [interview, planning, rounds]
skills: [communication]
---

## Why it matters

Most people fail an interview round they did not know existed. One candidate studied only ARIMA and then had to design a system. Do not repeat this. In this lesson you learn the **six rounds** of a typical time-series or forecasting ML interview. You learn what each round tests and how to prepare for it. Then you can spend your study time where it pays the most.

## The six rounds

A company may skip or merge rounds. The names change. The skills tested stay the same.

| # | Round | Length | What it tests |
|---|---|---|---|
| 1 | Recruiter screen | 20–30 min | Your story, level, salary range, visa, timing |
| 2 | Coding / [[OA]] | 60–90 min | Python, pandas, and small algorithms under a clock |
| 3 | ML fundamentals | 45–60 min | Metrics, bias and variance, leakage, model choice |
| 4 | Time-series deep dive | 45–60 min | Stationarity, seasonality, backtests, ARIMA vs ML |
| 5 | ML system design | 45–60 min | A whole forecasting system, from data to monitoring |
| 6 | Behavioural | 45 min | Teamwork, conflict, impact, ownership |

An **OA** (online assessment) is a timed test you take alone, on a web page, before you talk to a person. Many companies use it as a filter.

```chart
{"title": "Typical minutes per round (bars 1 to 6, in the table order)", "x": "round", "height": 220,
 "series": [
   {"name": "minutes", "kind": "bar", "y": [25, 75, 50, 50, 50, 45], "x": [1, 2, 3, 4, 5, 6]}
 ],
 "caption": "Round 2 (coding or OA) is the longest. Round 1 is the shortest but still decides if you continue."}
```

```check
{"q": "Which round is a timed test that you take alone, usually before you speak to an engineer?", "type": "single",
 "options": ["Recruiter screen", "Online assessment (OA)", "System design", "Behavioural round"],
 "answer": 1,
 "why": ["The recruiter screen is a call with a person.", "Correct: an OA is a timed online test, done alone.", "System design is a conversation with an interviewer at a whiteboard or document.", "The behavioural round is a conversation about your past work."]}
```

## What each round really looks for

**Coding / OA.** The grader runs your code on hidden tests. Correct and fast beats clever. For time series, expect four patterns:

- pandas wrangling (missing dates, groups, merges)
- metrics written from scratch (MAE, WAPE, MASE)
- leakage-free features (rolling mean that does not see the future)
- window algorithms (rolling max, longest run)

**ML fundamentals.** The interviewer asks short "why" questions. "Why not a random split?" "Why is MAPE a bad metric for zero sales?" Your answer must be short and exact.

**Time-series deep dive.** Here they test if you think in time. Can you explain a [[backtest]]? Can you say why a [[baseline]] comes first? Do you know when ARIMA beats a neural network?

**ML system design.** You get a vague prompt like "forecast demand for 2,000 stores". You must ask questions first. You then walk through data, models, evaluation, serving, and monitoring.

**Behavioural.** They check if you can work with other people. Stories with numbers win.

```check
{"q": "An interviewer says: 'Forecast demand for all our stores.' What is the best first move?", "type": "single",
 "options": ["Start drawing a neural network", "Ask who uses the forecast, for what decision, and how far ahead", "Say which library you prefer", "Ask how many GPUs you can use"],
 "answer": 1,
 "why": ["A model choice before the goal is a red flag.", "Correct: the decision, the user, and the horizon shape every later choice.", "Library talk is too early and says little about your thinking.", "Compute limits matter later, after the goal is clear."]}
```

## Level changes the weight

The rounds stay the same from junior to staff. The weight changes.

- **Junior or mid:** coding and fundamentals count most. System design may be light.
- **Senior:** system design and the time-series deep dive count most. You must show real trade-offs.
- **Staff and above:** the problem itself is vague. You must choose the question, not only the answer. See the Staff+ track in this course for more.

```check
{"q": "Which statement about seniority is the best summary?", "type": "single",
 "options": ["Seniors skip coding rounds", "Rounds are the same, but design and judgement weigh more as level grows", "Staff candidates only do behavioural rounds", "Juniors never get a design round"],
 "answer": 1,
 "why": ["Many senior loops still have a coding round.", "Correct: the weight moves toward design, trade-offs, and judgement.", "Staff candidates still face technical rounds.", "Some junior loops include a light design round."]}
```

## Make a prep plan from your weak rounds

Rate yourself from 1 (weak) to 5 (strong) for each round. Give the weakest rounds the most hours. Keep one hour per week for every round, so you do not forget a strong one. The code below does this with simple numbers.

## Worked example

You have 10 hours per week. Each round has a self-score. The weaker the score, the more hours it gets.

```python
# Share the weekly hours by "weakness" (5 - score), with at least 1 hour per round.
scores = {"coding_oa": 2, "ml_fundamentals": 4, "ts_deep_dive": 3,
          "system_design": 1, "behavioural": 4}
hours_total = 10
base = 1                                   # every round gets 1 hour
weak = {k: 5 - v for k, v in scores.items()}   # weakness points
spare = hours_total - base * len(scores)   # hours left to share
total_weak = sum(weak.values())
plan = {k: base + spare * w / total_weak for k, w in weak.items()}
for k, h in sorted(plan.items(), key=lambda kv: -kv[1]):
    print(f"{k:16s} {h:.1f} h")
# Output:
# system_design    2.8 h
# coding_oa        2.4 h
# ts_deep_dive     1.9 h
# ml_fundamentals  1.5 h
# behavioural      1.5 h
```

How it works: `weak` turns a high score into a low weight. Each round keeps its base hour, and the 5 spare hours are shared by weakness.

## Common mistakes

- Studying only models and ignoring the coding round.
- Practising on your own laptop with no clock. In an OA you have 25 minutes per problem.
- Skipping the behavioural round because "I am technical".
- Giving a model name before you ask about the goal.
- Having no story with numbers for your own projects.

## Interview lens

**Typical question:** "Walk me through how you would prepare a forecast for a new product line."

**Strong answer:** "First I ask what decision the forecast supports and the horizon. Then I check the data: how much history, how many series, which holidays. I build a seasonal naive baseline and a backtest with several origins. Only then I try ETS, LightGBM, or a foundation model, and I compare each with the baseline. I report error by segment, and I set up monitoring before launch."

**Red flags:** naming a model in the first sentence; no baseline; a random train/test split; no mention of who uses the forecast.

## Real world

- Public interview guides describe loops with a recruiter call, a coding round, a machine-learning round, a design round, and a behavioural round. The names differ by company.
- Online assessments are often run on platforms such as HackerRank or CodeSignal. The format is a timed set of coding tasks with hidden tests.

## Key points

- A forecasting loop has six rounds: recruiter, coding/OA, ML fundamentals, time-series deep dive, system design, behavioural.
- Each round tests a different skill, so prepare each one on purpose.
- Seniors are judged more on design and judgement than on syntax.
- Share your study hours by weakness, but touch every round every week.
