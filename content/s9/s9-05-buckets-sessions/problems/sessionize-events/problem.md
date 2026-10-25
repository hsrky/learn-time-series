---
slug: sessionize-events
title: Sessionize Events (Pure Python)
difficulty: Medium
type: function
tags: [sessions, python, sorting]
skills: [streaming-algorithms]
packages: []
companies_style: []
---
You get a list `events` of `(user, ts)` tuples. `user` is a string and `ts` is an integer number of seconds. The list is not sorted.

A user's events belong to the same **session** when each gap between neighbouring events (sorted by time) is **at most 1800 seconds**. A gap **greater than** 1800 starts a new session.

Return a list of `(user, start, end, count)` tuples, one per session, sorted by user and then by start. `start` and `end` are the first and last timestamps of the session and `count` is the number of events. Duplicate events with the same user and time are all counted.

### Example 1
**Input:** `events = [('ann', 0), ('ann', 300), ('ann', 4200), ('bob', 100)]`
**Output:** `[('ann', 0, 300, 2), ('ann', 4200, 4200, 1), ('bob', 100, 100, 1)]`
**Explanation:** Ann has a gap of 3900 s (more than 1800) before her third event, so she has two sessions.

### Constraints
- 0 <= len(events) <= 10^5
- 0 <= ts <= 10^9

### Hints
1. Sort the events: `sorted(events)` sorts by user and then by time.
2. Keep the current session as a list `[user, start, end, count]`.
3. Start a new one if the user changed or `ts - end > 1800`.

### Solution explanation
**Approach.** Sort by (user, time). Walk once. If the event continues the current session (same user, gap <= 1800) update `end` and `count`; otherwise append a new session.

**Why it works.** After sorting, sessions are contiguous runs, so one pass finds all of them.

**Complexity.** O(n log n) time for the sort, O(n) for the pass. Memory O(n) for the result.

**Common bugs.** Not sorting; using `>=` for the gap; merging sessions of different users; mutating tuples.
