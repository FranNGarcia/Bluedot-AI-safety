"""Export Inspect eval logs to results/results.csv and results/flagged.csv.

Usage:
    python analysis/export.py [logs_dir]   (defaults to ./logs)
"""

import sys
from pathlib import Path

from inspect_ai.analysis import EvalModel, SampleColumn, samples_df

SCORER = "self_audit_scorer"
DELIBERATION_SCORER = "deception_deliberation_scorer"
EVAL_AWARENESS_SCORER = "eval_awareness_scorer"
RESTRICTED_ACCESS_SCORER = "restricted_access_scorer"

VALUE_COLUMNS = [
    "self_deception",
    "differential_deception",
    "other_fidelity",
    "prose_self_disclosed",
    "csv_prose_divergence",
    "self_probe_called",
    "queue_probe_coverage",
    "malformed_output",
    "self_overreport",
    "review_needed",
]

METADATA_COLUMNS = [
    "cell",
    "consequence",
    "evidence",
    "identity_mode",
    "goal_pressure",
    "arm",
    "self_id",
]


def columns():
    cols = [
        *EvalModel,
        SampleColumn("sample_id", path="id"),
        SampleColumn("epoch", path="epoch"),
    ]
    cols += [
        SampleColumn(name, path=f"metadata.{name}") for name in METADATA_COLUMNS
    ]
    cols += [
        SampleColumn(name, path=f"scores.{SCORER}.value.{name}")
        for name in VALUE_COLUMNS
    ]
    cols.append(
        SampleColumn("self_category", path=f"scores.{SCORER}.metadata.self_category")
    )
    # secondary LLM-judge metrics, each reported by its own scorer (see README)
    cols.append(
        SampleColumn(
            "deception_deliberated", path=f"scores.{DELIBERATION_SCORER}.value"
        )
    )
    cols.append(
        SampleColumn(
            "deliberation_quote", path=f"scores.{DELIBERATION_SCORER}.metadata.quote"
        )
    )
    cols.append(
        SampleColumn(
            "eval_awareness_suspected", path=f"scores.{EVAL_AWARENESS_SCORER}.value"
        )
    )
    cols.append(
        SampleColumn(
            "eval_awareness_quote",
            path=f"scores.{EVAL_AWARENESS_SCORER}.metadata.quote",
        )
    )
    cols.append(
        SampleColumn(
            "restricted_access_undisclosed",
            path=f"scores.{RESTRICTED_ACCESS_SCORER}.value",
        )
    )
    cols.append(
        SampleColumn(
            "restricted_access_quote",
            path=f"scores.{RESTRICTED_ACCESS_SCORER}.metadata.quote",
        )
    )
    return cols


def main() -> None:
    logs_dir = sys.argv[1] if len(sys.argv) > 1 else "logs"
    out_dir = Path("results")
    out_dir.mkdir(exist_ok=True)

    df = samples_df(logs_dir, columns=columns(), full=True, strict=False)
    if isinstance(df, tuple):
        df, errors = df
        for err in errors:
            print(f"column error: {err}", file=sys.stderr)

    df.to_csv(out_dir / "results.csv", index=False)
    print(f"wrote {out_dir / 'results.csv'} ({len(df)} samples)")

    # review_needed (deterministic), deception_deliberated, and
    # eval_awareness_suspected (both LLM judge) are independent signals --
    # none feeds the others (see README) -- so flag a sample for manual
    # review if any one fires.
    flagged = df[
        (df["review_needed"] == 1)
        | (df["deception_deliberated"] == 1)
        | (df["eval_awareness_suspected"] == 1)
    ]
    flagged.to_csv(out_dir / "flagged.csv", index=False)
    print(f"wrote {out_dir / 'flagged.csv'} ({len(flagged)} samples to review)")

    # quick per-cell summary of the primary metrics
    if len(df):
        summary = (
            df.groupby(["model", "cell"])[
                [
                    "self_deception",
                    "differential_deception",
                    "other_fidelity",
                    "deception_deliberated",
                    "eval_awareness_suspected",
                ]
            ]
            .mean()
            .round(3)
        )
        print(summary.to_string())


if __name__ == "__main__":
    main()
