# WP11 — AI tutor (Claude Artifact build only)

Research summary (artifact runtime contract 0.2.75):

- A published Claude Artifact may declare runtime capabilities. `sample` lets the page **ask Claude**
  on the *viewer's own* Claude account: `const sample = await claude.use("sample")` → `null` when
  unavailable (any static host, or not granted). `await sample(input, {onText, signal, modelTier,
  cache, tools})` streams text; `sample.json(...)` returns parsed JSON. Each call is memoryless —
  the page sends instructions + context + the chat turns itself. First call asks the viewer for
  consent; errors are one rejected `{code, message, text?}` (hide on `not_granted` /
  `sampling_disabled`, back off on `rate_limited`, never retry in a loop).
- `tools` (page functions Claude may call) work where `sample.limits()` reports `tools`.
- `db` + `user` give per-viewer server-side storage (`data/users/<id>/…` is private to that user),
  so progress can follow the learner across devices when the site runs as an Artifact.
- On every other host `window.claude` does not exist → all of this is hidden and the site works
  exactly as before. **Never** block first paint on `claude.use()`; light features up when it resolves.

## Pedagogy rules for the tutor (put these in the standing instruction turn)

The tutor is a **coach, not an answer machine** (worked-example + desirable-difficulty research):

1. Plain English, CEFR B1, short sentences, define terms; if the learner set a "help language",
   answer in that language but keep technical terms in English with the translation in brackets.
2. Ground every answer in the context the page sends (lesson text, problem statement, learner code,
   judge results). Say "I am not sure" instead of inventing facts, numbers or APIs.
3. For problems: never write the full solution unless the learner pressed "Show me a solution".
   Prefer: a question back, the smallest next hint, pointing at the exact failing line/case.
4. Short answers (≤ 150 words) unless asked for more. Use small code snippets (≤ 6 lines).
5. End with one quick check question when it helps memory (retrieval practice).

## Features

| Where | Feature | Call |
|---|---|---|
| Header | "AI tutor" chip — shows only when `sample` resolves; opens a right drawer (bottom sheet on mobile) | — |
| Drawer | Chat with context of the current page (lesson section text / problem + code + last result). Quick buttons depend on page. Stop button. Clear chat. History per page kept in memory (and localStorage, best effort). | `sample(turns, {cache:false, onText, signal})`, tier `default` |
| Lesson step | "Explain simpler" and "Explain in my language" on each concept chunk | `sample(prompt, {modelTier:"quick", cache:{gcTime: 86400000}})` |
| Check / quiz | After a wrong answer: "Why is my answer wrong?" | quick tier |
| Workspace | "Explain my error" (failing case, got vs expected, traceback, code) → diagnosis + smallest hint | default tier, `cache:false` |
| Workspace | "Give me another hint" (beyond the 3 static hints; sends hints already shown) | default |
| Workspace | After Accepted: "Review my code like an interviewer" → complexity, pandas idioms, edge cases, 2 follow-up questions | default |
| Workspace | Tool `run_python({code})` (only if `limits().tools`): the tutor can run a tiny snippet in the learner's Python worker to show a value (5 s limit, output ≤ 4 KB) | tools |
| Drills | "Mock interviewer": after the learner submits a drill, the AI asks 3 follow-up questions one by one, then grades all sections against the rubric with `sample.json` → `{"scores":[{"item","score","why"}], "summary", "next_steps"}` | complex tier |
| Interview prep | "Mock interview chat": choose level (junior / senior / staff) and topic; interviewer asks one question at a time, gives feedback after each answer | default |
| Settings | Help language (English default; list of ~15 common languages), tutor on/off | — |

Progress sync (optional, phase 2): when `db` and `user` resolve, store the progress blob at
`data/users/<id>/progress/main` (debounced, at most one write per 10 s, only on change) and merge on
load (newest `updatedAt` per item wins). localStorage stays the primary store; db is a mirror.

## Artifact manifest

`capabilities: {sample: {}, db: {}, user: {}}` (no images). Republish keeps it when omitted.

## Engineering notes

- One module `site/js/ai.js` + `site/js/pages/ai-drawer.js`; everything behind `TSP.AI.ready`.
- Context builder trims to ~12 KB: lesson section text (strip HTML), problem description, learner
  code (≤ 8 KB), last result (first failing case + error).
- Error copy map per code; hide the feature on permanent codes for the rest of the view.
- A fake `window.claude` shim for local testing only (`?ai=mock`), never shipped as active.
- The engine on the Artifact: one wheel (statsmodels, 31 MB) is over the 15 MB per-file limit →
  publish it split into `*.part0..N`; the worker intercepts `fetch` for that wheel name and
  concatenates the parts (a manifest `engine/split.json` lists them). Static hosts use the
  unsplit file (the worker tries the whole file first, then parts).
