# WP5 status: S6 Deep learning for TS + S7 Foundation models & LLMs

Legend: ⬜ todo, 🟨 in progress, ✅ done. Problem result = `tools/check_problem.py` (all "ok").
Build check: full `tools/build.py --strict` on a scratch copy of s6+s7: 0 warnings, 0 errors.

## S6 (10 lessons, 8 problems; minimum 8 / 7)

| Lesson | Status | Problem(s) | check_problem |
|---|---|---|---|
| s6-01-windowed-datasets | ✅ | make-sliding-windows | ok |
| s6-02-rnn-lstm-gru | ✅ | rnn-cell-forward | ok |
| s6-03-tcn-causal-convolutions | ✅ | causal-conv1d | ok |
| s6-04-seq2seq-deepar | ✅ | gaussian-nll | ok |
| s6-05-nbeats-nhits | ✅ | nbeats-residual-stack | ok |
| s6-06-temporal-fusion-transformer | ✅ | none | - |
| s6-07-transformers-for-ts (Informer, Autoformer, PatchTST, iTransformer) | ✅ | patchify-series | ok |
| s6-08-are-transformers-effective (DLinear/NLinear) | ✅ | dlinear-forward | ok |
| s6-09-revin-normalization | ✅ | revin-normalize | ok |
| s6-10-state-space-models (S4/Mamba) | ✅ | none | - |

## S7 (7 lessons, 5 problems; minimum 6 / 4)

| Lesson | Status | Problem(s) | check_problem |
|---|---|---|---|
| s7-01-what-is-a-foundation-model | ✅ | none | - |
| s7-02-chronos-family (widget chronos-tokens) | ✅ | chronos-tokenizer | ok |
| s7-03-other-foundation-models (TimesFM 2.5, Moirai 2.0, zoo) | ✅ | none | - |
| s7-04-zero-shot-finetune-routers | ✅ | fm-router-select | ok |
| s7-05-benchmarking-honestly | ✅ | zero-shot-eval-harness, weighted-quantile-loss | ok, ok |
| s7-06-llms-and-forecasting-agents | ✅ | llmtime-digit-encoding | ok |
| s7-07-when-not-to-use | ✅ | none | - |

## Validation done
- 13/13 problems ok (reference passes, starter fails, 2-3 visible cases, seeded larger case).
- All worked-example python blocks run; `# Output:` blocks were generated from real output.
- All quiz.json / cards.json / glossary.s6.json / glossary.s7.json parse; every single/multi question has one `why` per option.
- Every [[term]] has a glossary entry (s6: 30 terms, s7: 5 terms).
- Staff lens in: s6-07, s6-08, s6-09, s6-10, s7-02 to s7-07.

## Cautions / not finished
- Facts about Mistral "Timestral" and IBM FlowState are deliberately left vague (no reliable details). TIME benchmark is also described only as "check its paper".
- Chronos-2 / Moirai 2.0 / TimesFM 2.5 details are limited to what the brief states plus widely known points; the lessons tell learners to check model cards and dates.
- Widget `chronos-tokens` is used with empty params; check it renders with the app's defaults.
