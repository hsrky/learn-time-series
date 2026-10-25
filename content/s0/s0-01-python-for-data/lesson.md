---
id: s0-01-python-for-data
title: Welcome! Python for data in one hour
minutes: 25
level: beginner
goals: [Understand how this portal works, Use lists and dicts to hold data, Write loops and functions, Build a new list with a comprehension]
prereqs: []
tags: [python, basics, welcome]
skills: [pandas-fluency]
---
## Why it matters

Welcome to **TimeSeries Path**. You do not need any experience. We start from zero and go step by step.

A [[time series]] is a list of numbers measured over time. Your phone step count is one. So is the temperature each hour.

To work with these numbers we use Python. This lesson teaches only the small part of Python that you need.

## How this portal works

Each lesson follows the same four steps. This is called a **learning loop**.

1. **Learn.** Read a short chunk. Look at the chart next to it.
2. **Check.** Answer a quick question. You get feedback at once, also for wrong answers.
3. **Practice.** Solve a small coding problem. The judge runs your code in your browser.
4. **Review.** Short flashcards come back after 1, 2, 4, 8 and 16 days. This is called [[spaced repetition]].

You can skip anything. Nothing is locked. A lesson is **mastered** when the quiz is 80% or higher and the problem is accepted.

```check
{"q": "You answered a question wrongly. What does the portal do?", "type": "single",
 "options": ["Nothing, you must guess again", "It explains why each option is right or wrong", "It locks the next lesson"],
 "answer": 1,
 "why": ["No. Every question gives feedback.", "Correct. Feedback on each option helps you learn from mistakes.", "No. Nothing is ever locked."]}
```

## Lists and dicts

A [[list]] keeps values in order. Think of daily step counts for one week.

You read one value with its **position**, called an [[index]]. Python counts from 0. So `steps[0]` is the first day.

A [[dict]] (dictionary) keeps pairs of **key** and **value**. Use it when you look up by name, not by position.

```python
steps = [4200, 5100, 3900, 6000, 7200, 8100, 2500]  # one week of steps

print(steps[0])      # first day
print(steps[-1])     # last day (negative counts from the end)
print(steps[1:4])    # a slice: positions 1, 2, 3 (4 is not included)
print(len(steps))    # how many values

best = {"day": "Sat", "steps": 8100}   # a dict
print(best["day"])
# Output:
# 4200
# 2500
# [5100, 3900, 6000]
# 7
# Sat
```

```chart
{"title": "Steps per day for one week", "x": "day", "height": 200, "kind": "bar",
 "series": [{"name": "steps", "y": [4200, 5100, 3900, 6000, 7200, 8100, 2500]}],
 "caption": "Seven numbers in a list. Position 0 is the first bar."}
```

```check
{"q": "steps = [10, 20, 30, 40]. What is steps[1:3]?", "type": "single",
 "options": ["[10, 20]", "[20, 30]", "[20, 30, 40]"],
 "answer": 1,
 "why": ["That would be steps[0:2].", "Correct. A slice starts at position 1 and stops before position 3.", "That would be steps[1:]."]}
```

## Loops and functions

A [[loop]] repeats work for each value. A [[function]] is a named block of code. You give it inputs and it returns a result.

Here is a function that finds the average. We use a loop to add the values.

```python
def average(values):
    """Return the mean of a list of numbers."""
    total = 0
    for v in values:          # visit each value once
        total = total + v     # add it to the running total
    return total / len(values)

steps = [4200, 5100, 3900, 6000, 7200, 8100, 2500]
print(average(steps))
# Output:
# 5285.714285714285
```

Indented lines belong to the block above them. Python uses **indentation** (4 spaces) instead of brackets.

```check
{"q": "What does return do inside a function?", "type": "single",
 "options": ["Prints the value on screen", "Sends the result back to the caller and stops the function", "Starts the loop again"],
 "answer": 1,
 "why": ["That is print. return gives the value to the code that called the function.", "Correct. The caller can store the result in a variable.", "No. A loop repeats by itself."]}
```

## Comprehensions

A [[list comprehension]] builds a new list in one line. It is a short form of a loop.

Pattern: `[expression for item in list if condition]`.

```python
steps = [4200, 5100, 3900, 6000, 7200, 8100, 2500]

thousands = [s / 1000 for s in steps]            # change every value
active = [s for s in steps if s >= 5000]         # keep only some values
print(thousands)
print(active)

# A dict comprehension: day name -> steps
days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
by_day = {d: s for d, s in zip(days, steps)}     # zip walks two lists together
print(by_day["Fri"])
# Output:
# [4.2, 5.1, 3.9, 6.0, 7.2, 8.1, 2.5]
# [5100, 6000, 7200, 8100]
# 7200
```

```check
{"q": "Which line keeps only the values above 10 from the list x?", "type": "single",
 "options": ["[v for v in x if v > 10]", "[v > 10 for v in x]", "[v in x if 10]"],
 "answer": 0,
 "why": ["Correct. The if part filters the values.", "This builds a list of True and False, not the values.", "This is not valid logic."]}
```

## Worked example

Task: a sensor gives hourly temperatures. Some readings are `None` (missing). Count the missing ones, then compute the average of the valid ones.

```python
readings = [18.5, 19.0, None, 21.2, None, 22.8, 23.1]

# Step 1: keep only real numbers
valid = [r for r in readings if r is not None]

# Step 2: count the missing values
n_missing = len(readings) - len(valid)

# Step 3: wrap the average in a function so we can reuse it
def mean(values):
    return sum(values) / len(values)   # sum() adds a whole list

print("missing:", n_missing)
print("mean:", round(mean(valid), 2))
# Output:
# missing: 2
# mean: 20.92
```

You will see the same idea again in numpy and pandas. They do it faster and with less code.

## Common mistakes

- Using position 1 for the first value. Python starts at 0.
- Forgetting `return`. The function then gives back `None`.
- Dividing by `len(values)` when the list is empty. This raises an error.
- Changing a list while you loop over it. Build a new list instead.
- Mixing tabs and spaces in indentation.

## Interview lens

**Typical question:** "Given a list of numbers with some missing values (`None`), return the mean of the valid ones."

**Strong answer:** Filter first with a list comprehension. Then divide the sum by the count of valid values. Say what you return when no valid value exists, for example `None` or `nan`. Name the time and space cost: one pass, O(n). Mention that with pandas `Series.mean()` skips missing values for you.

**Red flags:**
- Dividing by the full length instead of the valid count.
- Not handling the empty case.
- Writing a long loop when a comprehension is clear.

## Real world

- Python is the most common language in forecasting work. The libraries you will meet in this course (numpy, pandas, scikit-learn, statsmodels) are all open source Python packages.
- Many online coding assessments for data roles let you choose Python and test your list and dict skills first.

## Key points

- The portal loop is **learn, check, practice, review**. Nothing is locked.
- A list keeps ordered values. Positions start at 0. Slices stop before the end position.
- A dict looks up values by key.
- A function takes inputs and returns a result. A comprehension builds a list in one line.
