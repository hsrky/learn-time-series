---
id: s14-08-design-docs-and-strategy
title: Writing a design doc and a tech strategy
minutes: 30
level: staff
goals: [Write a decision-ready design doc with goals, non-goals, alternatives and risks, Use a weighted decision matrix and know its limits, Write a short tech strategy with diagnosis, guiding policy and actions, Run a review that ends in a decision]
prereqs: [s14-03-build-buy-foundation]
tags: [staff, design-doc, strategy, RFC, writing]
skills: [staff, communication]
---

## Warm-up

```check
{"q": "From the build-vs-buy lesson: what is the first step when a hard limit like latency exists?", "type": "single",
 "options": ["Compare cost first", "Remove options that break the hard limit, then compare cost", "Ignore the limit", "Choose the cheapest option"],
 "answer": 1,
 "why": ["An infeasible option cannot win on cost.", "Correct.", "Hard limits cannot be ignored.", "The cheapest may be infeasible."]}
```

```check
{"q": "What is a golden backtest set?", "type": "single", "options": ["A frozen set of series and periods used to compare models", "The newest data only", "A set used to tune every model", "A list of the best models"], "answer": 0, "why": ["Correct: it stays fixed so that results are comparable.", "It is frozen, not always the newest data.", "Tuning on it would spoil it.", "It is a data set, not a list of models."]}
```

## Why it matters

At staff level, much of your impact comes through **writing**. A good document lets 30 people make the same decision without 30 meetings. A bad one starts a long argument. Two documents matter most: the **design doc** (one project, one decision) and the **tech strategy** (a direction for a year or more). Both must be short, clear and honest about trade-offs.

## The design doc

A design doc answers: "What do we build, why, and what else did we consider?" Use this outline. Aim for 3 to 6 pages.

| Section | What goes in |
|---|---|
| Context | The problem and the decision it supports, with numbers (volume, cost, deadline) |
| Goals and non-goals | What must be true at the end; what we will **not** do |
| Proposal | The design in plain words, one diagram, the key interfaces |
| Alternatives | Two or three other options and why not |
| Evaluation | How we will know it works: metrics, backtest, pilot |
| Risks and mitigations | What could go wrong; fallbacks; guard-rails |
| Rollout and cost | Stages, owners, dates, run cost |
| Open questions | What you still need from reviewers |

Two sections do most of the work: **non-goals** (they stop scope growth) and **alternatives** (they show you thought about the choice).

```check
{"q": "Which section protects a project from growing without end?", "type": "single",
 "options": ["Context", "Non-goals", "Open questions", "Rollout"],
 "answer": 1,
 "why": ["Context sets the problem.", "Correct: non-goals state what is out of scope.", "Open questions invite input.", "Rollout is about stages."]}
```

## Decision matrix: use it, but carefully

A **weighted decision matrix** scores each option on criteria with weights. It makes the trade-offs visible and the discussion about weights, not about opinions.

Steps: choose 4 to 6 criteria; agree the weights first (before you score); score each option from 1 to 5; multiply and sum.

Limits: scores are subjective; the sum hides a deal-breaker (a score of 1 on risk can be fatal). So add **must-have** criteria that remove an option, and look at the best and worst scores, not only the total. Run a **sensitivity check**: if a small change in weights flips the winner, say so.

```chart
{"title": "Weighted scores of three options (see the worked example)", "x": "option (1 = extend, 2 = new platform, 3 = buy)", "height": 220,
 "series": [
   {"name": "weighted score", "kind": "bar", "x": [1,2,3], "y": [3.85, 3.15, 3.45]}
 ],
 "caption": "Extending the current pipeline wins on this scoring. A small change in the weights could change this, so check sensitivity."}
```

```check
{"q": "Option A scores 4.2 in total but has a 1 out of 5 on security, a must-have. What do you do?", "type": "single",
 "options": ["Choose A, the total is highest", "Reject or fix A, because a must-have criterion failed", "Change the weights until A wins", "Ignore security"],
 "answer": 1,
 "why": ["A total can hide a deal-breaker.", "Correct: must-haves are filters, not weights.", "Changing weights after the fact is bias.", "Security is a must-have here."]}
```

## The tech strategy

A strategy is not a list of wishes. A useful structure (from Richard Rumelt's work on strategy) has three parts, called the **kernel**:

1. **Diagnosis.** What is the real problem? Be specific and honest. Example: "Eight teams run separate pipelines. 40% of engineer time is spent on data plumbing. Numbers from finance and operations disagree by up to 8%."
2. **Guiding policy.** The overall approach, including what we choose **not** to do. Example: "One shared platform for standard forecasts; custom models allowed only through the shared backtest and contracts."
3. **Coherent actions.** A few steps that support each other, with owners and dates. Example: "Q1: data contracts for two teams. Q2: backtest service. Q3: managed path. Q4: retire two old pipelines."

A strategy needs **trade-offs**. If it says "yes" to everything, it is not a strategy.

```check
{"q": "Which statement is a guiding policy (not a goal)?", "type": "single",
 "options": ["Improve forecast accuracy", "Standard forecasts run on the managed path; custom models are allowed only through the shared backtest and data contracts", "Be the best team", "Use more AI"],
 "answer": 1,
 "why": ["A goal, with no approach.", "Correct: it is an approach that rules out some actions.", "A wish.", "A slogan."]}
```

## Reviews that end in a decision

- Send the doc **before** the meeting. Use the meeting for disagreements only.
- Name a **decider** and a date.
- Keep a **decision log**: date, decision, reasons, who agreed, when to revisit.
- Ask reviewers for specific input: "Is the rollback plan enough?" and not "Thoughts?".
- Close the loop: after launch, check the doc's claims against results and write what you learned.

## Worked example

The decision matrix from the chart, with a simple sensitivity check on the weight of impact.

```python
criteria = ["impact", "risk", "time_to_value", "cost", "team_fit"]
weights = {"impact": 0.35, "risk": 0.20, "time_to_value": 0.20, "cost": 0.15, "team_fit": 0.10}
scores = {   # 1 (bad) to 5 (good); for risk and cost, 5 means low risk / low cost
    "extend current":  {"impact": 3, "risk": 4, "time_to_value": 5, "cost": 4, "team_fit": 4},
    "new platform":    {"impact": 5, "risk": 2, "time_to_value": 2, "cost": 2, "team_fit": 3},
    "buy vendor":      {"impact": 4, "risk": 3, "time_to_value": 4, "cost": 3, "team_fit": 2},
}

def total(opt, w):
    return sum(w[c] * scores[opt][c] for c in criteria)

for opt in scores:
    print(f"{opt:15s} {total(opt, weights):.2f}")

# sensitivity: raise the weight of impact to 0.60 and share the rest in proportion
w2 = {c: weights[c] * (1 - 0.60) / (1 - weights["impact"]) for c in criteria}
w2["impact"] = 0.60
best = max(scores, key=lambda o: total(o, w2))
print("best if impact weighs 0.60:", best, round(total(best, w2), 2))
# Output:
# extend current  3.85
# new platform    3.15
# buy vendor      3.45
# best if impact weighs 0.60: new platform 3.86
```

With the original weights, extending the current pipeline wins. If impact becomes much more important, the answer changes. That is useful to say in the review: "The decision depends on how much we value impact over speed."

## Common mistakes

- A design doc with no alternatives.
- No non-goals, so the scope grows.
- Documents of 20 pages that nobody reads.
- Weights chosen after seeing the scores.
- A strategy that is only a list of projects.
- No decision log, so old arguments return.
- Writing for yourself and not for the reader's decision.

## Interview lens

**Typical question:** "How do you decide on a technical direction for a team, and how do you get agreement?"

**Strong answer:** "I write a short design doc. It states the problem with numbers, goals and non-goals, the proposal, and two or three real alternatives. I use a decision matrix for the trade-offs, but I set weights before scoring, I add must-have filters, and I test sensitivity. I share the doc early with the people it affects, ask for specific feedback, and name a decider and a date. After the decision I keep a log and I revisit it at a set time, comparing results with the claims in the doc."

**Red flags:** only meetings, no writing; no alternatives; a strategy without trade-offs.

## Real world

- Many engineering teams use design docs and RFCs (requests for comments). The public essay "Design Docs at Google" by Malte Ubl describes a common structure and why teams write them.
- Richard Rumelt's book "Good Strategy / Bad Strategy" (2011) introduced the kernel of diagnosis, guiding policy and coherent actions. Will Larson's public writing on staff engineering applies it to technology strategy.

## Staff lens

Write the document you wish someone had given you. A new engineer should be able to read your strategy in 10 minutes and know what to do and what not to do. Keep a one-page version. Update it each half year, and delete what is no longer true.

## Key points

- A design doc has context, goals and non-goals, proposal, alternatives, evaluation, risks, rollout and open questions.
- Use a decision matrix with weights set first, must-have filters, and a sensitivity check.
- A tech strategy has a diagnosis, a guiding policy that excludes some actions, and coherent actions.
- End reviews with a decider, a date, and a decision log.
