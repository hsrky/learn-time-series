# Brief for content authors (WP2–WP8)

1. Read fully: docs/DESIGN.md (esp. §1 learning design, §1.1 plain-English rules, §2 curriculum, §2.1 skills),
   docs/CONTENT_GUIDE.md (exact formats), tools/harness.py (how problems are judged).
2. Write ONLY inside your own stage folders (content/sN/...). New glossary terms go in
   content/sN/glossary.sN.json. Do not edit other folders, docs/PLAN.md, tools/, or site/.
   Do not git commit or push.
3. Keep a live checklist in docs/status/<WP>.md: one row per lesson and per problem with status
   (⬜/🟨/✅) and the check_problem.py result. Update it after each lesson.
4. Validate every problem as you go:
   VENV=<path to a Python venv with numpy 2.0.2, pandas 2.2.3, scipy 1.14.1, statsmodels 0.14.4, scikit-learn 1.6.1, markdown>
   $VENV/bin/python tools/check_problem.py content/sN
   All must print "ok". Also run each worked-example ```python block with $VENV/bin/python and
   make sure the "# Output:" comment matches what it really prints.
5. Validate JSON files parse (`$VENV/bin/python -m json.tool file`), and that every ```check/quiz
   question has a `why` entry per option.
6. Quality bar for a lesson (this is what the learner sees — it is the product):
   - A complete beginner can follow it in ONE pass. Plain English, B1 level, short sentences,
     every term defined at first use and marked [[term]] with a glossary entry.
   - Concrete numbers first, then the idea, then the formula with each symbol explained.
   - At least one ```chart or ```widget per lesson, placed next to the text it explains.
   - A ```check after each concept chunk. Mastery quiz with ≥ 2 scenario questions.
   - Worked example: real, runnable, commented code with true output.
   - Interview lens: "Typical question" + "Strong answer" (3–6 sentences) + "Red flags".
   - Real world: only public, well-known facts (papers, competitions, engineering blogs). Never
     invent numbers, dates or quotes. If unsure, state the idea without specifics.
   - Problems: LeetCode quality — clear statement, examples, constraints, 3 hints, solution
     explanation with complexity, edge-case tests, a seeded random larger case. Prefer problems
     that a real time-series OA would ask (pandas wrangling, from-scratch algorithms, metrics,
     leakage-free feature building, backtests).
7. Use time wisely: aim to meet the lesson/problem minimums in docs/PLAN.md for your stages.
   Breadth of the curriculum list matters (every bullet in DESIGN §2 for your stages must be
   covered by a lesson or a clear section), but never at the cost of correctness.
8. Final message: a short report — lessons and problems created (counts per stage), validation
   results, anything you could not finish.
