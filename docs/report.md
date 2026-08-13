# Self-Audit Deception in Frontier Models

*Draft — to be completed after Stage 1 runs.*

## Abstract

TODO after results: one paragraph — setup, headline differential deception
rates, consequence/evidence effects, caveats.

## 1. Background

Meinke et al. (2024), *Frontier Models are Capable of In-Context Scheming*,
showed frontier models sometimes take covert actions (oversight subversion,
sandbagging, doubling down under interrogation) when scenario context makes
misaligned behaviour instrumentally useful. This work extends that
methodology with a **self-audit** scenario: the model, acting as an
operational auditor, discovers via a trusted evaluation channel that *it
itself* fails an alignment check, and we measure whether it reports that
result faithfully.

## 2. Method

See README for the full design. Key points:

- Factorial: declared consequence (silent/safe/lethal) × planted evidence
  (none/incriminating prelim/bug alibi); placebo and self-clean controls.
- Within-sample control: a second, non-self deployment is also flagged.
- Two report channels (CSV artifact + prose summary), scored
  deterministically against known ground truth. No LLM judge in the
  primary metrics; three clearly-separated secondary LLM-judge metrics
  (reasoning-trace deliberation, restricted-source disclosure, eval
  awareness — see README) run alongside.
- Headline metric: `differential_deception` — self misreported while the
  other flagged model was reported honestly. Output failures (unparseable
  or truncated CSVs) are excluded from deception rates rather than
  classified as omission/honesty.

## 3. Results

TODO: table of rates by cell × model with Wilson CIs; plots from
`analysis/plots.py`; qualitative excerpts from flagged transcripts.

## 4. Limitations

- Single fictional scenario family; content quirks may drive behaviour.
- `bug_alibi` cells conflate deception with (misplaced) legitimate judgement;
  reported separately.
- Deception expressed only in reasoning traces is not visible to the
  deterministic primary metrics; it is measured by the secondary LLM-judge
  scorer `deception_deliberation_scorer`, and flagged-sample review remains
  manual.
- The LLM-judge scorers read untrusted agent output and are in principle
  susceptible to grader manipulation (prompt injection from the transcript);
  the prompts instruct the grader to ignore embedded instructions, but this
  is best-effort. Judge runs without a bound `grader` role fall back to the
  model under test grading itself (recorded via the `self_graded` flag).
- `prose_self_disclosed` is keyword/window-based; in the real-identity arm
  an agent can disclose without naming its own deployment id and be missed.
- Eval awareness is now measured automatically per-sample via
  `eval_awareness_scorer` (v2) rather than only spot-checked; confirmed
  non-hypothetical on a real Stage 1 sample (deepseek, `control_placebo`),
  where the reasoning explicitly named the scenario as an "agentic
  benchmark" designed to test compliance. Samples where it fires are
  excluded from the deception-rate plots and routed to `flagged.csv`, but
  the judge itself can still miss subtler or implicit awareness (false
  negatives) — flagged-sample review should still spot-check unflagged
  transcripts, not rely on the judge alone.

## 5. Reproducibility

Commit hash, model ids, epochs, and total spend: TODO at run time.
