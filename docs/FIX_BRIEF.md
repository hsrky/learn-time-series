# Brief for the review-fix pass (after WP10)

Read docs/REVIEW.md (the findings, with file/line lists), docs/DESIGN.md §1.1 (plain-English rules)
and docs/CONTENT_GUIDE.md. Fix only files in your assigned stages, only these file types:
lesson.md, quiz.json, cards.json, drill.json, problems/*/problem.md (prose only).
Do NOT edit glossary.*.json (another agent owns them), tools/, site/, or other stages.
Do NOT change code blocks (```python / ```notebook), tests.py, solution.py, starter.py.
Do not git commit.

Fixes:
1. Replace every listed idiom / phrasal verb (rule of thumb → "simple guide"/"common guideline",
   deep dive → "detailed look", under the hood → "inside", etc.). Grep your stages for the full
   idiom list in REVIEW.md §2 — fix all hits, also in cards/quiz/check/problem text.
2. Rewrite sentences longer than 20 words in prose (not code, tables or headings): split them into
   two or three short sentences. Required: zero sentences over 25 words in your stages; as few as
   possible over 20. Keep the meaning and every [[term]] marker exactly.
3. Split concept chunks over ~150 words into two `##` concept sections (each with its own short
   title), placed before `## Worked example`. If you split, add a ```check after the new chunk only
   if the chunk teaches a new idea. Keep the required section order.
4. Every lesson except s0-01 must have **2** ```check questions in `## Warm-up` (recall from
   prerequisites / earlier stages, with `why` for every option).
5. Keep facts unchanged unless the review flags them; never add new numbers or claims.

Validate after each lesson: JSON blocks parse; then at the end run
`OMP_NUM_THREADS=1 $VENV/bin/python tools/build.py --skip-judge` (VENV in AUTHOR_BRIEF.md) and make
sure there are 0 errors and no new warnings for your stages. Measure with a script: count prose
sentences > 20 and > 25 words per lesson before and after, and report the numbers.
Final message: before/after counts per stage, and anything you could not fix.
