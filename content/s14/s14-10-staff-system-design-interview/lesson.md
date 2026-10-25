---
id: s14-10-staff-system-design-interview
title: The staff-level system design interview
minutes: 40
level: staff
goals: [Show the differences between senior and staff design answers, Go deep on two or three risky parts with numbers, List failure modes and a migration plan, Practise with the three Staff+ drills]
prereqs: [s14-07-reliability-and-postmortems, s14-03-build-buy-foundation]
tags: [staff, interview, system-design, migration, deep-dive]
skills: [staff, scale, production, communication]
---

## Warm-up

```check
{"q": "From the reliability lesson: which is the best guard-rail against a large loss when a forecast drives automatic buying?", "type": "single",
 "options": ["More features", "An exposure limit and a kill switch", "A bigger model", "A weekly slide"],
 "answer": 1,
 "why": ["Does not cap loss.", "Correct.", "Does not cap loss.", "Does not cap loss."]}
```

## Why it matters

The senior design interview asks: "Can you design this system?" The staff interview asks: "Can you decide what to build, for whom, with which risks, and how to get it done by many people?" You are expected to lead the conversation, not follow a checklist. You will use the six-part frame from the earlier lesson ([[lesson:s13-06-ml-system-design-rubric]]), but with more depth and more judgement.

## What changes at staff level

| Senior answer | Staff answer |
|---|---|
| Solves the problem as given | Questions the problem; checks it is the right one |
| One good design | Two or three options with trade-offs and a recommendation |
| Technical detail everywhere | Deep dives where risk is highest; the rest at a glance |
| Rough numbers | Numbers for scale, cost, latency and error, with assumptions |
| Failure modes listed | Failure modes ranked by impact and likelihood, with mitigations |
| Ends at launch | Includes migration, roll-out, ownership, org impact, and success metrics |
| Works alone | Says who must be involved and how to get them aligned |

```check
{"q": "Which behaviour is typical of a staff-level answer?", "type": "single",
 "options": ["Starting to draw the architecture at once", "Questioning the premise, offering options with a recommendation, and planning the migration and ownership", "Naming many tools", "Avoiding numbers"],
 "answer": 1,
 "why": ["Drawing first skips framing.", "Correct.", "Tools are not decisions.", "Numbers are expected."]}
```

## A 45-minute map

| Minutes | Content |
|---|---|
| 0–8 | Frame: decision, users, cost of error, scale, constraints; state assumptions |
| 8–15 | Options and recommendation at a high level (diagram, one slide of text) |
| 15–32 | **Two or three deep dives** on the riskiest parts, with numbers |
| 32–40 | Failure modes, monitoring, rollback, migration |
| 40–45 | Org: ownership, staffing, roadmap, success metrics; questions |

Choose deep dives yourself and say why: "I will go deep on evaluation and on the migration, because those carry most risk."

## Deep dives with numbers

For each deep dive, use three layers: **mechanism** (how it works), **numbers** (how big, how fast, how costly), **failure** (how it breaks and what we do).

Example deep dive: scoring a foundation model for 1 million daily series.

- Mechanism: batch inference on GPUs, series grouped by length, results written to a table.
- Numbers: if one GPU scores about 500 series per second (an assumption you must measure), 1 million series take 2,000 seconds, about 33 minutes. With 4 GPUs: about 8 minutes.
- Failure: the GPU job fails or is slow, so the fallback is last night's forecast or seasonal naive; an alert fires.

```chart
{"title": "Staged roll-out of a new model (percent of series served by the new model, by week)", "x": "week", "height": 220,
 "series": [
   {"name": "new model share (%)", "x": [1,2,3,4,5,6,7,8,9,10,11,12], "y": [0,0,5,5,10,25,25,50,50,75,100,100]}
 ],
 "marks": [{"x": 3, "label": "canary starts"}],
 "caption": "Weeks 1-2: shadow mode (0% served). Then a small canary, then steps with a check before each step."}
```

```check
{"q": "One GPU scores 250 series per second. How many minutes for 600,000 series on one GPU?", "type": "numeric",
 "answer": 40, "tol": 0.01,
 "why": "600,000 / 250 = 2,400 seconds = 40 minutes."}
```

## Failure modes: rank them

List 6 to 8 failure modes, then rank by **impact × likelihood**. Pick the top three and give a mitigation for each. Typical forecast-system failures:

- Silent data errors (late or wrong inputs).
- Leakage in a new feature that looks great offline.
- Regime change (a shock).
- A vendor or model version change.
- Feedback loops (the decision changes the data).
- Capacity or cost overrun.
- Organisational: a team does not adopt it, or the owner leaves.

```check
{"q": "Which failure mode is both likely and costly for an automatic ordering system that uses a new foundation model?", "type": "single",
 "options": ["The chart colour", "A version change that shifts forecasts without anyone noticing", "A typo in a comment", "A meeting delay"],
 "answer": 1,
 "why": ["No impact.", "Correct: silent shifts affect all orders. Pin versions and monitor bias and coverage.", "No impact.", "Low impact."]}
```

## Migration plan

Replacing a legacy system is mostly a **migration**, not a modelling task.

1. **Inventory:** who uses the old forecasts, in which format, for which decision?
2. **Parity first:** build the new path to give at least the old quality on the golden backtest.
3. **Shadow mode:** run both, compare for several weeks, including special periods.
4. **Canary and ramp:** serve 5% of series (a mix of segments), then 25%, 50%, 100%, with checks and a rollback at each step.
5. **Cut-over and clean-up:** switch consumers, keep the old path for a short period, then remove it. Remove it for real: dead systems create risk.
6. **Communicate:** to users, with dates and what changes for them.

## Practise with the three drills

Use the timed drills in this track.

1. [[lesson:s14-02-forecasting-platform]]: a global forecasting platform for many teams.
2. [[lesson:s14-06-probabilistic-decisions]]: forecast-driven inventory for 10,000 SKUs.
3. This lesson: **replace legacy models with a foundation model: plan and risks**.

After each drill, score yourself with the rubric. Write down where you gave a senior answer and where a staff answer was possible.

## Worked example

Compute the inference time and cost of a nightly foundation-model job, with the assumptions written as variables so you can change them in the interview.

```python
n_series = 1_000_000
series_per_sec_per_gpu = 500          # assumption: measure this on your data and context length
n_gpus = 4
gpu_cost_per_hour = 2.0               # assumption: example price
nights_per_month = 30

seconds = n_series / (series_per_sec_per_gpu * n_gpus)
minutes = seconds / 60
gpu_hours = n_gpus * seconds / 3600
cost_per_night = gpu_hours * gpu_cost_per_hour
cost_per_month = cost_per_night * nights_per_month

print(f"job time: {minutes:.1f} minutes on {n_gpus} GPUs")
print(f"GPU hours per night: {gpu_hours:.2f}")
print(f"cost per night: {cost_per_night:.2f}")
print(f"cost per month: {cost_per_month:.0f}")
print(f"cost per 1,000 forecasts: {cost_per_night / n_series * 1000:.4f}")
# Output:
# job time: 8.3 minutes on 4 GPUs
# GPU hours per night: 0.56
# cost per night: 1.11
# cost per month: 33
# cost per 1,000 forecasts: 0.0011
```

The job is small and cheap if the throughput assumption holds. Say so, and add: "The real risk is not compute. It is evaluation, covariates, and migration." That shows judgement.

## Common mistakes

- Jumping into architecture before framing.
- One design, no alternatives.
- Going deep everywhere, so nothing is deep.
- No numbers, or numbers without assumptions.
- Ignoring migration, ownership and people.
- A long list of failure modes with no ranking.
- No success metric for the project itself.

## Interview lens

**Typical question:** "Our legacy forecasting models are old. Leadership wants to replace them with a foundation model. Plan it."

**Strong answer:** "First I ask what problem we want to solve: accuracy, cost, maintenance, or cold start. Then I describe three options: keep the legacy models, replace them fully, or a hybrid where the foundation model covers cold start and long-tail series. I would test on a golden backtest with seasonal naive and the legacy model, by segment, with covariates. If the gain is clear in some segments only, I recommend the hybrid. I size the job: for a million series it is a small GPU job. I list the top risks: silent version changes, loss of covariate features, evaluation leakage from pre-training data, and organisational adoption. The plan: shadow mode, canary, staged ramp with rollback, then retire the old path. I define success as lift over the legacy model and lower maintenance cost."

**Red flags:** "just swap it"; no test; no migration plan; ignoring covariates and version pinning.

## Real world

- Teams that moved from classical statistical models to global machine-learning models, such as in the M5 competition, found that features and careful evaluation mattered more than the choice of algorithm.
- Public model cards and papers for foundation models such as Chronos, TimesFM and Moirai show zero-shot results on benchmarks. Practitioners recommend checking these on their own data before replacing production models.

## Staff lens

In a staff interview, people listen for **judgement under uncertainty**. Say what you do not know and how you would find out. Say which decision is reversible (try it) and which is not (needs more care). End with how you would measure the success of the whole effort.

## Key points

- Staff answers question the premise, compare options, and recommend one.
- Spend most time on two or three deep dives: mechanism, numbers, failure.
- Rank failure modes by impact times likelihood and give mitigations.
- Migration plan: inventory, parity, shadow, canary and ramp, cut-over, clean-up, communication.
- Practise with the three Staff+ drills and score yourself.
