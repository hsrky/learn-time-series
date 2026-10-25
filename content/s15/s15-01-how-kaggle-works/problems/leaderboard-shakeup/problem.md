---
slug: leaderboard-shakeup
title: Public vs Private Leaderboard Shake-up
difficulty: Easy
type: function
tags: [kaggle, leaderboard, ranking, pandas]
skills: [backtest, pandas-fluency]
packages: []
companies_style: [Kaggle competitions]
---
In a Kaggle competition each team has two scores. The **public** score uses a small part of the test data and is visible all the time. The **private** score uses the rest and is revealed at the end. The final ranking uses the private score. When teams overfit the public score, their rank changes a lot at the end. This is called a **shake-up**.

Write `leaderboard_shakeup(teams, public, private)`.

- `teams`: list of team names.
- `public`, `private`: lists of error scores in the same order (**lower is better**).

Compute the rank of each team on each leaderboard. Rank 1 is the lowest score. Teams with the same score share the best (smallest) rank of the tie (for example scores 0.5, 0.5, 0.7 give ranks 1, 1, 3).

Return a DataFrame with columns `team, public_rank, private_rank, rank_change`, where `rank_change = public_rank − private_rank` (positive means the team moved **up**). Sort by `private_rank`, then by `team`. The index is `0, 1, 2, ...`.

### Example 1
**Input:**
```
teams   = ["A", "B", "C"]
public  = [0.10, 0.20, 0.30]
private = [0.40, 0.20, 0.10]
```
**Output:**
```
team  public_rank  private_rank  rank_change
C     3            1             2
B     2            2             0
A     1            3            -2
```
**Explanation:** Team A led the public board but is last on the private board. Team C climbed two places.

### Constraints
- 0 ≤ number of teams ≤ 10^5
- Scores are floats; ties are possible

### Hints
1. Put the data into a DataFrame with `pd.DataFrame`.
2. `Series.rank(method="min")` gives the tie rule from the statement.
3. Convert ranks to integers, compute the change, and sort with `sort_values(["private_rank", "team"])`.

### Solution explanation
Ranking with `method="min"` gives tied teams the smallest rank of their group. The rank change is a simple subtraction. Sorting by private rank (then name) makes the order stable and clear. Time O(n log n).

Common bugs: using the default `method="average"` (it gives 1.5 for ties), sorting scores in the wrong direction (higher score is worse here), and forgetting that a positive change means the team moved up.
