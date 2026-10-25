---
id: s9-05-buckets-sessions
title: Time buckets and sessionization
minutes: 30
level: intermediate
goals: [Assign events to time buckets, Sessionize events with a 30-minute gap, Do both in pure Python and in pandas]
prereqs: []
tags: [sessionization, buckets, pandas]
skills: [streaming-algorithms, pandas-fluency]
---
## Warm-up
```check
{"q": "Which pandas call turns hourly rows into daily totals?", "type": "single", "options": ["s.resample('D').sum()", "s.rolling(24).sum()", "s.shift(24)"], "answer": 0, "why": ["Correct.", "Rolling keeps the hourly rows.", "Shift moves values; it does not group them."]}
```
```check
{"q": "What does `df.groupby('user')['ts'].diff()` give?", "type": "single", "options": ["The time since the previous row of the same user", "The total time of each user", "The first time of each user"], "answer": 0, "why": ["Correct.", "That is a sum or a max-min.", "That is first()."]}
```

## Why it matters
Raw event logs have one row per click, per payment, or per sensor message. To analyse them you need **buckets** (how many events per minute?) and **sessions** (which clicks belong to one visit?). Both are favourite OA tasks: they test your handling of time, order and edge cases, in pure Python and in pandas.

## Time buckets
A **[[bucket]]** is a fixed time interval. For timestamps in seconds and a bucket size `b` seconds, the bucket start is:

`bucket_start = (ts // b) * b`

- `//` = integer division (drops the fraction)
- `b` = bucket size in seconds, for example 60 for minutes

Example: b = 60, ts = 125 → 125 // 60 = 2 → start = 120. Timestamps 120 to 179 share this bucket.

**Empty buckets matter.** If no event happens in a minute, the count is 0, not "missing". Charts and models need those zeros.

```check
{"q": "b = 300 seconds, ts = 1000. What is the bucket start?", "type": "numeric", "answer": 900, "tol": 0.01, "why": "1000 // 300 = 3, and 3 × 300 = 900."}
```

## Sessions: a gap starts a new session
A **[[session]]** is a group of events by one user where the pause between two neighbouring events is **at most** a limit (here 30 minutes = 1800 seconds). A pause **longer** than the limit starts a new session.

Example, one user, times in minutes: 0, 5, 20, 70, 80, 200.
Gaps: 5, 15, 50, 10, 120. Gaps over 30 are 50 and 120, so there are **3 sessions**: {0, 5, 20}, {70, 80}, {200}.

Pure Python plan (O(n log n) because of sorting):
1. Sort by user, then time.
2. Walk through. If the user changes, or the [[gap]] is more than the limit, start a new session. Otherwise extend the current one.

```chart
{"title": "Events of one user: gaps over 30 minutes split sessions", "x": "minute", "height": 190, "series": [{"name": "event", "x": [0, 5, 20, 70, 80, 200], "y": [1, 1, 1, 1, 1, 1], "kind": "dots"}], "marks": [{"x": 45, "label": "gap 50 > 30"}, {"x": 140, "label": "gap 120 > 30"}], "caption": "Six events, three sessions."}
```

```check
{"q": "Gap rule: limit 30 minutes. Two events are exactly 30 minutes apart. Same session?", "type": "single", "options": ["Yes, only gaps greater than 30 split", "No, 30 or more splits", "Depends on the user"], "answer": 0, "why": ["Correct: the rule says 'greater than'. Always check whether the limit is inclusive.", "That is a different rule (>=).", "The rule is the same for all users."]}
```

## The same in pandas: diff, compare, cumsum
1. Sort by user and time.
2. `gap = df.groupby('user')['ts'].diff()` (the first event of each user gives NaT).
3. `new = gap.isna() | (gap > pd.Timedelta(minutes=30))` marks the first event of every session.
4. `session = new.groupby(df['user']).cumsum()` numbers the sessions inside each user (1, 2, 3, ...).
5. `df.groupby(['user', 'session']).agg(start=('ts', 'min'), end=('ts', 'max'), events=('ts', 'size'))`.

The key trick: **a flag, then a [[cumulative sum]], gives a group number**. You will use it again for gaps and islands.

```check
{"q": "What does `flag.cumsum()` do when flag is 1 at the start of each session and 0 otherwise?", "type": "single", "options": ["Gives a session number to every row", "Counts the events in total", "Removes the first events"], "answer": 0, "why": ["Correct: the number increases at every new session start.", "The total would be the last value only.", "Nothing is removed."]}
```

## Worked example
Sessions in pure Python and in pandas give the same answer.

```python
import pandas as pd

events = [("ann", 0), ("ann", 300), ("ann", 1200), ("ann", 4200), ("ann", 4800), ("bob", 100), ("bob", 9000)]
LIMIT = 1800                                           # 30 minutes in seconds

# --- pure Python
sessions = []                                          # [user, start, end, n]
for user, ts in sorted(events):
    last = sessions[-1] if sessions else None
    if last and last[0] == user and ts - last[2] <= LIMIT:
        last[2] = ts                                   # extend the current session
        last[3] += 1
    else:
        sessions.append([user, ts, ts, 1])             # start a new session
print(sessions)

# --- pandas
df = pd.DataFrame(events, columns=["user", "ts"]).sort_values(["user", "ts"])
gap = df.groupby("user")["ts"].diff()
df["session"] = (gap.isna() | (gap > LIMIT)).groupby(df["user"]).cumsum()
out = df.groupby(["user", "session"])["ts"].agg(start="min", end="max", events="size").reset_index()
print(out.values.tolist())

# Output:
# [['ann', 0, 1200, 3], ['ann', 4200, 4800, 2], ['bob', 100, 100, 1], ['bob', 9000, 9000, 1]]
# [['ann', 1, 0, 1200, 3], ['ann', 2, 4200, 4800, 2], ['bob', 1, 100, 100, 1], ['bob', 2, 9000, 9000, 1]]
```

## Common mistakes
- Not sorting first. The gap logic only works on sorted times.
- Mixing up `>` and `>=` for the gap rule.
- Computing gaps across users (forgetting `groupby('user')`).
- Dropping empty buckets, or using `resample` and forgetting the time zone.
- Using float seconds for the bucket start and getting rounding errors. Use integer division.

## Interview lens
**Typical question:** "Given click events with a user and a [[timestamp]], group them into sessions with a 30-minute inactivity limit."

**Strong answer:** I sort by user and time. A new session starts when the user changes or the gap to the previous event is larger than 30 minutes. In plain Python I do this in one pass and keep the current session. In pandas I compute the gap with `groupby().diff()`, mark session starts, and use a cumulative sum to number the sessions. The time is O(n log n) for the sort and [[O(n)]] for the pass. I confirm whether the limit is inclusive and how to treat duplicate timestamps.

**Red flags:** sessions across different users; no sorting; a double loop over all events.

## Real world
- Web analytics tools commonly define a session by inactivity; the standard default in Google Analytics (Universal Analytics) was a 30-minute timeout.
- Stream processors such as Apache Flink offer "session windows" that close after a gap of inactivity.

## Key points
- Bucket start = `(ts // size) * size`. Keep empty buckets with count 0.
- A session ends when the gap to the next event is larger than the limit. Sort first, per user.
- In pandas: `diff`, compare, `cumsum` gives the session number.
- Cost: O(n log n) for sorting, O(n) for the pass.
