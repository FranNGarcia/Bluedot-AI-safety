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
  deterministically against known ground truth. No LLM judge.
- Headline metric: `differential_deception` — self misreported while the
  other flagged model was reported honestly.

## 3. Results

TODO: table of rates by cell × model with Wilson CIs; plots from
`analysis/plots.py`; qualitative excerpts from flagged transcripts.

## 4. Limitations

- Single fictional scenario family; content quirks may drive behaviour.
- `bug_alibi` cells conflate deception with (misplaced) legitimate judgement;
  reported separately.
- Deterministic scoring cannot detect deception expressed only in reasoning
  traces; flagged-sample review is manual.
- Eval awareness was not automatically measured in v1 (spot-checked).

## 5. Reproducibility

Commit hash, model ids, epochs, and total spend: TODO at run time.
