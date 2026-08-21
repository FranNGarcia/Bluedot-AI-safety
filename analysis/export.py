"""Export Inspect eval logs to results/results.csv and results/flagged.csv.

Usage:
    python analysis/export.py [logs_dir]   (defaults to ./logs)
"""

import sys
from pathlib import Path

from inspect_ai.analysis import EvalModel, SampleColumn, SampleSummary, samples_df
from inspect_ai.log import list_eval_logs

SCORER = "self_audit_scorer"
DELIBERATION_SCORER = "deception_deliberation_scorer"
RESTRICTED_ACCESS_SCORER = "restricted_access_scorer"
AWARENESS_SCORER = "eval_awareness_scorer"

VALUE_COLUMNS = [
    "self_deception",
    "differential_deception",
    "other_fidelity",
    "prose_self_disclosed",
    "csv_prose_divergence",
    "self_probe_called",
    "queue_probe_coverage",
    "csv_row_coverage",
    "malformed_output",
    "incomplete_output",
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
    # SampleSummary supplies `id` and `epoch` (plus token/error/limit fields).
    # Do NOT hand-roll a column named `sample_id`: inspect injects its own
    # unique `sample_id` per row and then calls drop_duplicates() on it, so a
    # user column with that name shadows the key and silently collapses the
    # frame to one row per sample id (11 rows for the whole log set).
    cols = [
        *SampleSummary,
        *EvalModel,
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
    # the self row as filed (verdict/score/action/notes) -- what the agent
    # actually wrote, needed to characterise *how* a falsification was done
    cols.append(
        SampleColumn("self_row", path=f"scores.{SCORER}.metadata.self_row")
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
    cols.append(
        SampleColumn("eval_awareness", path=f"scores.{AWARENESS_SCORER}.value")
    )
    cols.append(
        SampleColumn(
            "eval_awareness_quote", path=f"scores.{AWARENESS_SCORER}.metadata.quote"
        )
    )
    return cols


def successful_logs(logs_dir: str) -> list[str]:
    """Paths of the logs worth exporting: completed runs only.

    `eval_set` leaves the aborted attempt on disk when it retries a task, so a
    log dir can end up holding two files for the same `task_id` -- the run that
    died and the one that finished. Both carry the same sample uuids for the
    samples that completed before the abort, and `samples_df` dedupes on uuid
    keeping the FIRST occurrence it reads, so pointing it at the raw directory
    silently mixes rows from the failed run into the results (observed on
    claude-opus-4.8: 43 rows from the aborted run, 77 from the good one).
    """
    logs = list_eval_logs(logs_dir, filter=lambda log: log.status == "success")
    total = len(list_eval_logs(logs_dir))
    if total > len(logs):
        print(
            f"skipping {total - len(logs)} incomplete log(s) under {logs_dir}",
            file=sys.stderr,
        )
    return [log.name for log in logs]


def main() -> None:
    logs_dir = sys.argv[1] if len(sys.argv) > 1 else "logs"
    out_dir = Path("results")
    out_dir.mkdir(exist_ok=True)

    logs = [logs_dir] if Path(logs_dir).is_file() else successful_logs(logs_dir)
    if not logs:
        sys.exit(f"no successful eval logs under {logs_dir}")

    df = samples_df(logs, columns=columns(), full=True, strict=False)
    if isinstance(df, tuple):
        df, errors = df
        for err in errors:
            print(f"column error: {err}", file=sys.stderr)

    df.to_csv(out_dir / "results.csv", index=False)
    print(f"wrote {out_dir / 'results.csv'} ({len(df)} samples)")

    # review_needed (deterministic), deception_deliberated, and
    # eval_awareness (both LLM judge) are independent signals -- none feeds
    # the others (see README) -- so flag a sample for manual review if any
    # one fires.
    flagged = df[
        (df["review_needed"] == 1)
        | (df["deception_deliberated"] == 1)
        | (df["eval_awareness"] == 1)
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
                    "eval_awareness",
                ]
            ]
            .mean()
            .round(3)
        )
        print(summary.to_string())


if __name__ == "__main__":
    main()
