---
id: s15-01-how-kaggle-works
title: How Kaggle time-series competitions work
minutes: 30
level: intermediate
goals: [Read a Kaggle competition page and name its parts, Explain public and private leaderboards and why shake-ups happen, Build a time-based validation that mimics the test period, Use Kaggle notebooks and the submit workflow without wasting quota]
prereqs: []
tags: [kaggle, leaderboard, validation, notebooks, leakage]
skills: [backtest, leakage, baseline-first]
---

## Warm-up

```check
{"q": "Why must a forecasting validation set come after the training data in time?", "type": "single", "options": ["To be faster", "To avoid using the future to predict the past", "To have more rows", "It is a Kaggle rule only"], "answer": 1, "why": ["No.", "Correct.", "No.", "It is a general rule."]}
```
```check
{"q": "What is data leakage?", "type": "single", "options": ["Losing data files", "Using information at training time that is not available at prediction time", "Missing values", "A slow model"], "answer": 1, "why": ["No.", "Correct.", "No.", "No."]}
```

## Why it matters

Kaggle is the best free gym for forecasting. You get real data, a clear metric, a public ranking, and the solutions of the winners. The Kaggle lab in this course follows six competitions step by step. Before you start, you need to know the rules of the game. The most common mistake is to chase the public leaderboard and to fall many places at the end. This lesson explains how the competitions work and how to protect yourself.

## Parts of a competition

Open a competition page. You always find these parts.

| Part | What it is |
|---|---|
| **Overview** | The task, the metric, the timeline, the prizes |
| **Data** | `train` files, a `test` file with no answers, and a `sample_submission` |
| **Code** | Public notebooks from other people |
| **Discussion** | Questions, ideas, and the host's answers |
| **Leaderboard** | The ranking of all teams |
| **Rules** | What data is allowed, team size, and daily submission limit |

Your job: read the metric, then predict the target for every row in `test`. You upload a CSV in the format of `sample_submission`. Kaggle scores it and shows the result.

Read the **Rules** page first. It tells you if external data is allowed, how many submissions you may send per day (often 5, check each competition), and how teams can share code.

```check
{"q": "Which file tells you the exact format of the CSV you must upload?", "type": "single",
 "options": ["train.csv", "test.csv", "sample_submission.csv", "the Discussion tab"],
 "answer": 2,
 "why": ["train.csv holds the examples with answers.", "test.csv holds the rows to predict, without answers.", "Correct: the sample submission shows the columns and ids.", "Discussion may help, but the file is the contract."]}
```

## Public and private leaderboard

Kaggle splits the test rows into two parts.

- The **public** part is scored every time you submit. Everyone sees it.
- The **private** part is hidden. It is scored once, at the end. **The final ranking uses the private score.**

If you tune your model to raise the public score, you may be fitting the noise of that small part. At the end, many teams move up or down. This is a **shake-up**.

Look at the chart. Each dot is a team with the same true skill. The dots do not lie on a line: the public rank says little about the private rank.

```chart
{"title": "30 equal teams: public rank (x) vs private rank (y)", "x": "public rank", "height": 260,
 "series": [
   {"name": "teams", "kind": "dots", "x": [2,15,9,6,26,5,19,30,10,13,22,21,8,14,27,7,20,18,1,28,16,4,12,25,17,24,3,23,29,11], "y": [22,21,18,5,12,8,25,30,6,9,28,15,19,10,27,29,4,14,3,16,2,17,7,23,20,13,1,11,26,24]}
 ],
 "caption": "Simulated data. If public rank predicted private rank, the dots would form a rising line. They look like a cloud."}
```

```check
{"q": "A team is first on the public leaderboard by a tiny margin. What does this tell you about the final rank?", "type": "single",
 "options": ["It will win", "Very little: the public part may be small and noisy", "It will be last", "Nothing can be known"],
 "answer": 1,
 "why": ["A tiny lead is often noise.", "Correct: be careful with small public differences.", "No reason to say last.", "Some information exists, but it is weak."]}
```

## Time-based splits: the test is the future

In forecasting competitions the test period is **after** the training period. For example, Store Sales asks for the 16 days after the last training day. A random split would let your model see days next to the test days, and your local score would be too good.

Do this instead:

1. Find the length of the test period (for example 16 days).
2. Hold out the **last** period of the same length from the training data (the **validation** set).
3. Train on everything before it. Score on the validation set with the competition metric.
4. Repeat with 2 or 3 earlier validation windows for a stable score. This is a [[backtest]].
5. Trust your local validation more than the public leaderboard.

Make the validation similar to the test: same length, same gap, same type of days (holidays, paydays).

```check
{"q": "The test period is the last 28 days after the training data. How should you build the validation set?", "type": "single",
 "options": ["Random 20% of rows", "The last 28 days of the training data, with training only on earlier days", "The first 28 days of the training data", "All data, no split"],
 "answer": 1,
 "why": ["A random split leaks neighbouring days.", "Correct: it mimics the test.", "Training on later data would leak the future.", "No split means no honest score."]}
```

## Leakage and the rules

[[data leakage]] in Kaggle has two meanings.

- **Your leakage:** using information in your features that is not available at prediction time (for example a rolling mean that includes today's value). It ruins your validation.
- **Competition leaks:** a hidden pattern in the data (for example row order or ids) that predicts the target but means nothing in real life. Hosts often forbid or fix them. Read the rules and discussions.

Also follow the rules: do not use the test labels, do not share private code outside your team, and use external data only if the rules allow it.

## Kaggle notebooks

Kaggle gives free notebooks in the browser.

- **Data:** attach the competition data. It appears under `/kaggle/input/<competition-name>/`.
- **Output:** files you write to `/kaggle/working/` are saved with the notebook version.
- **Hardware:** CPU is free. GPU and TPU have a **weekly quota** of hours. Check the number in your account. Start on CPU, and use a GPU only for neural networks.
- **Sessions** stop after some hours or when idle. Save versions often.
- **Submit:** run `submission.csv` creation, then use "Submit to competition" on the notebook, or the command line: `kaggle competitions submit -c <name> -f submission.csv -m "message"`.
- In **code competitions** internet is switched off in the notebook. Attach datasets and models instead of downloading them.

```notebook
# A minimal Kaggle notebook header for this course (run on Kaggle)
import os
import numpy as np
import pandas as pd

# See which files are attached under /kaggle/input
for root, dirs, files in os.walk("/kaggle/input"):
    for f in files[:10]:
        print(os.path.join(root, f))
```

```check
{"q": "Where should your notebook save submission.csv so that Kaggle keeps it?", "type": "single",
 "options": ["/kaggle/input/", "/kaggle/working/ (or the notebook's current working directory)", "/tmp/only/", "Nowhere; it keeps nothing"],
 "answer": 1,
 "why": ["Input is read-only.", "Correct: the working directory is saved as the notebook output.", "Temporary files can be lost.", "Output files are kept."]}
```

## Worked example

We simulate 30 teams with the same true skill. The public part is small, so its noise is large. The private part is larger, so its noise is smaller. We compare the ranks.

```python
import numpy as np

rng = np.random.default_rng(7)
n_teams = 30
skill = rng.normal(0.50, 0.01, n_teams)           # true error of each team (lower is better)
public = skill + rng.normal(0, 0.02, n_teams)     # small public part: noisy
private = skill + rng.normal(0, 0.005, n_teams)   # large private part: less noisy

pub_rank = public.argsort().argsort() + 1         # 1 = best
pri_rank = private.argsort().argsort() + 1

print("correlation of ranks:", round(float(np.corrcoef(pub_rank, pri_rank)[0, 1]), 2))
print("average rank shift:", float(np.abs(pub_rank - pri_rank).mean()))
i = int(np.where(pub_rank == 2)[0][0])
print("team at public rank 2 ends at private rank", int(pri_rank[i]))
# Output:
# correlation of ranks: 0.39
# average rank shift: 7.6
# team at public rank 2 ends at private rank 22
```

The rank shift is large although every team is the same in skill. Real competitions have real skill differences, but a small public set still adds noise. Practise the ranking logic in [[problem:leaderboard-shakeup]].

## Common mistakes

- Using a random split for a forecasting task.
- Choosing the final submission by the best public score only.
- Sending 5 submissions per day to "probe" the public set.
- Not reading the rules (external data, team size).
- Burning GPU hours on a model that a CPU can train.
- Forgetting to save the notebook version that made the submission.

## Interview lens

**Typical question:** "You tried 100 variants on a Kaggle task. How do you pick the final one?"

**Strong answer:** "I trust a time-based validation that copies the test period, with several windows, more than the public leaderboard. I pick the model with the best average validation score and a stable error across windows, and I check that the public score is not far off. If two models are close, I choose the simpler one or blend them. The public score is a small, noisy sample, and I know that selecting the best of many tries gives an optimistic result."

**Red flags:** "I sorted by public score"; a random split; no mention of the selection effect.

## Real world

- Kaggle shake-ups are well known. Many competition write-ups describe teams that fell or rose many places when the private leaderboard was revealed, which is why experienced competitors rely on local cross-validation.
- The M5 forecasting competition on Kaggle (Walmart data, 2020) used a fixed future test period. Top solutions used careful time-based validation and global gradient boosting models.
- The Web Traffic competition had two stages: the final ranking was based on how well the models forecast a period that had not yet happened when the competition began.

## Key points

- A competition has train, test, sample submission, a metric, and rules. Read the rules first.
- The public leaderboard is a small noisy sample. The final ranking is private.
- In forecasting the test is the future, so validate with time-based windows that mimic it.
- Avoid leakage in your features and respect the rules about data and sharing.
- Use notebooks wisely: CPU first, save versions, write `submission.csv` to the working directory.
