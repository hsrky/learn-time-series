---
id: s14-09-influence-mentoring-roadmap
title: Influence without authority, mentoring and roadmap trade-offs
minutes: 30
level: staff
goals: [Move a group to a decision without being their manager, Mentor with the right level of help, Score roadmap items with a simple model and still use judgement, Say no to good ideas in a way people accept]
prereqs: [s14-08-design-docs-and-strategy]
tags: [staff, influence, mentoring, roadmap, RICE]
skills: [staff, communication]
---

## Warm-up

```check
{"q": "Which part of a design review makes sure the meeting ends with a choice?", "type": "single",
 "options": ["A long agenda", "A named decider and a date", "More attendees", "A bigger slide deck"],
 "answer": 1,
 "why": ["Length does not create decisions.", "Correct.", "More people make decisions slower.", "Slides do not decide."]}
```

```check
{"q": "What does forecast value add (FVA) measure?", "type": "single", "options": ["Whether a step makes the forecast better than the step before it", "The size of the model", "The number of series", "The cost of the server"], "answer": 0, "why": ["Correct.", "Size is not the question.", "Count is not the question.", "Cost is only one part of the decision."]}
```

## Why it matters

A staff engineer rarely has direct reports. Yet the job is to change what many teams do: which metric they use, which platform they build on, which risks they accept. You cannot order them. You must **influence**. You also grow other people (mentoring) and choose what the team will **not** do (roadmap). These are the skills that separate a strong senior engineer from a staff engineer.

## Influence without authority

Five habits that work.

1. **Start with their problem.** Ask what hurts them. Link your proposal to their goal, not yours.
2. **Build trust with small wins.** Fix a small, visible issue first. People follow people who deliver.
3. **Use shared facts.** Agree the metric and the baseline before the debate. A shared backtest ends many arguments.
4. **Pre-wire.** Talk to the key people one by one before the big meeting. No one should be surprised in public.
5. **Make adoption easy.** A template, a script, or a one-hour pairing session beats a long document.

Also, know when to **disagree and commit**: say your concern clearly once, then support the decision.

```check
{"q": "Two teams use different accuracy metrics. You want them to share one. What is the best first step?", "type": "single",
 "options": ["Send an email order", "Compute both teams' results on the same backtest, show the numbers, and ask what decision each needs", "Wait", "Escalate to the VP at once"],
 "answer": 1,
 "why": ["You have no authority to order.", "Correct: shared facts and their decisions create agreement.", "Waiting changes nothing.", "Escalation damages trust and is a last step."]}
```

## Mentoring

Mentoring means helping someone grow faster than they would alone. Match your help to their level.

| Their level on the task | Your style | Example |
|---|---|---|
| New | **Show.** Do it together, explain why | Pair on a first backtest |
| Learning | **Guide.** Ask questions, review early | "What baseline will you compare with?" |
| Capable | **Delegate.** Give the problem, check at milestones | They own the monitoring design |
| Expert | **Sponsor.** Give visibility and bigger scope | Recommend them to present to leadership |

Good habits: give feedback soon and specifically ("your backtest used a random split; use a time split because...") and explain the **why**. In code review, teach, do not only fix. Write down what you learned about their goals and check in monthly.

```check
{"q": "A capable engineer is stuck on an unclear problem. Which style is best?", "type": "single",
 "options": ["Take the task and do it yourself", "Ask guiding questions and help them frame the problem, then let them lead", "Say nothing", "Give a long lecture"],
 "answer": 1,
 "why": ["They will not grow.", "Correct: guide, do not take over.", "They stay stuck.", "A lecture does not build skill."]}
```

## Roadmap trade-offs

You always have more ideas than time. Use a simple scoring model to start the conversation. One popular model is **RICE**:

`RICE score = Reach × Impact × Confidence ÷ Effort`

- **Reach:** how many users, teams or stores are affected in a period.
- **Impact:** size of the effect per unit (for example 0.5 = low, 1 = medium, 2 = high).
- **Confidence:** how sure are you? (for example 50%, 80%, 100%)
- **Effort:** person-months.

The score is not the answer. It makes assumptions visible. Then apply judgement:

- **Dependencies.** Some items unlock others (data contracts before a platform).
- **Risk first.** Do the item that could kill the plan early.
- **Capacity.** Keep slack (for example 20%) for incidents and support.
- **Balance.** Mix quick wins, bets, and maintenance.

```chart
{"title": "RICE scores of four roadmap items (see the worked example)", "x": "item (1 contracts, 2 backtest service, 3 FM pilot, 4 real-time)", "height": 220,
 "series": [
   {"name": "RICE score", "kind": "bar", "x": [1,2,3,4], "y": [2.13, 3.2, 0.75, 0.17]}
 ],
 "caption": "The backtest service scores highest. The real-time item scores low: small reach, high effort, low confidence."}
```

```check
{"q": "Item: reach 10 teams, impact 2, confidence 0.5, effort 5 person-months. What is the RICE score?", "type": "numeric",
 "answer": 2, "tol": 0.01,
 "why": "10 × 2 × 0.5 / 5 = 10 / 5 = 2."}
```

## Saying no

You will have to say no. Do it in a way that keeps trust.

- Say **what you are choosing** and **why**: "We do X first because it reaches 8 teams."
- Offer an **alternative**: a template, a later date, or another team.
- Write down the **trigger** that would change the decision: "If volume doubles, we revisit."
- Keep the no list visible. It shows the team's real priorities.

```check
{"q": "A VP asks for a new real-time forecast. It scores low on RICE. Which reply is best?", "type": "single",
 "options": ["No.", "Yes, we will add it.", "Not this quarter: the backtest service reaches 8 teams and comes first. We can revisit if you can name a decision that needs real-time. Here is a batch alternative for now.", "Ask someone else."],
 "answer": 2,
 "why": ["Gives no reason or path.", "Overcommits and breaks other plans.", "Correct: reason, alternative, and trigger to revisit.", "Avoids responsibility."]}
```

## Worked example

RICE scoring in code, with sorted output. Change one assumption and see the rank move.

```python
items = [
    # name,                 reach, impact, confidence, effort (person-months)
    ("data contracts",         8,    1.0,    0.8,        3),
    ("backtest service",       8,    2.0,    0.8,        4),
    ("foundation model pilot", 3,    1.0,    0.5,        2),
    ("real-time serving",      1,    2.0,    0.5,        6),
]

def rice(r, i, c, e):
    return r * i * c / e

ranked = sorted(items, key=lambda x: -rice(*x[1:]))
for name, r, i, c, e in ranked:
    print(f"{name:24s} {rice(r, i, c, e):.2f}")

# What if confidence in the foundation model pilot rises to 0.9?
items[2] = ("foundation model pilot", 3, 1.0, 0.9, 2)
new = sorted(items, key=lambda x: -rice(*x[1:]))
print("top 2 after the change:", [x[0] for x in new[:2]])
# Output:
# backtest service         3.20
# data contracts           2.13
# foundation model pilot   0.75
# real-time serving        0.17
# top 2 after the change: ['backtest service', 'data contracts']
```

The ranking is stable at the top, so the first choice does not depend on one doubtful number. The pilot rises, but it does not beat the backtest service.

## Common mistakes

- Trying to win by authority or by escalation.
- Surprising people in a public meeting.
- Doing the work for a mentee.
- Giving feedback too late or too vague.
- Treating the RICE score as the final answer.
- Saying yes to everything, then missing all deadlines.
- A roadmap with 100% of capacity planned and no slack.

## Interview lens

**Typical question:** "Tell me about a time you got other teams to adopt your approach without being their manager."

**Strong answer:** "Three teams used three different accuracy metrics and nobody trusted the comparisons. I ran a shared backtest on their data, so the comparison was fair. I talked to each lead first about the decisions they make, and I learned that one team needed bias reported, so I added it. I wrote a one-page proposal, and ran a pairing session to move the first team in a day. Within a quarter, all three teams used the shared service, and our cross-team disputes about accuracy stopped."

**Red flags:** "I told them to"; no understanding of their needs; no measurable result.

## Real world

- The RICE model was described publicly by the product team at Intercom, and is widely used to compare roadmap items.
- Will Larson's public writing on staff engineers describes roles such as sponsor and mentor and the idea of influencing through writing and trust, not authority.

## Staff lens

Your influence is a budget. Spend it on a few important changes and not on every disagreement. Be generous with credit: when a team adopts your idea, say it was theirs. Over time, people bring problems to you early, which is the best sign of influence.

## Key points

- Influence comes from their problem, small wins, shared facts, pre-wiring and easy adoption.
- Mentor with the right style: show, guide, delegate, sponsor.
- Use RICE (Reach × Impact × Confidence ÷ Effort) to expose assumptions, then add judgement about dependencies, risk and slack.
- Say no with a reason, an alternative, and a trigger to revisit.
