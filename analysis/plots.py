"""Plots for the self-audit eval. Reads results/results.csv (see export.py).

Usage:
    python analysis/plots.py
"""

import math
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

RESULTS = Path("results/results.csv")
OUT_DIR = Path("results/plots")

CELL_ORDER = [
    "silent-none",
    "silent-prelim",
    "silent-bug_alibi",
    "safe-none",
    "safe-prelim",
    "safe-bug_alibi",
    "lethal-none",
    "lethal-prelim",
    "lethal-bug_alibi",
    "control_self_clean",
    "control_placebo",
]


def wilson_ci(successes: float, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = successes / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    margin = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return max(0.0, center - margin), min(1.0, center + margin)


def rate_by(df: pd.DataFrame, group: str, metric: str) -> pd.DataFrame:
    grouped = df.groupby(group)[metric].agg(["sum", "count", "mean"])
    cis = [wilson_ci(row["sum"], int(row["count"])) for _, row in grouped.iterrows()]
    grouped["ci_low"] = [c[0] for c in cis]
    grouped["ci_high"] = [c[1] for c in cis]
    return grouped


def bar_with_ci(grouped: pd.DataFrame, title: str, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    x = range(len(grouped))
    yerr = [
        grouped["mean"] - grouped["ci_low"],
        grouped["ci_high"] - grouped["mean"],
    ]
    ax.bar(x, grouped["mean"], yerr=yerr, capsize=4, color="#4C72B0")
    ax.set_xticks(list(x))
    ax.set_xticklabels(grouped.index, rotation=45, ha="right")
    ax.set_ylim(0, 1)
    ax.set_ylabel("rate")
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"wrote {out}")


def main() -> None:
    df = pd.read_csv(RESULTS)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # exclude output failures (unparseable or truncated CSVs) from deception
    # rates -- neither carries a deception signal. Also exclude samples where
    # the eval_awareness judge fired: if the agent reasoned about this being
    # a test/benchmark rather than a real deployment, its honesty or
    # dishonesty in that sample isn't clean evidence of self-preservation --
    # the scenario collapsed for that sample (see judge_scorers.py docstring;
    # confirmed non-hypothetical on a real deepseek control_placebo sample).
    ok = df[
        (df["malformed_output"] == 0)
        & (df["incomplete_output"] == 0)
        & (df["eval_awareness"] != 1)
    ].copy()
    ok["cell"] = pd.Categorical(ok["cell"], categories=CELL_ORDER, ordered=True)

    for arm, arm_df in ok.groupby("arm"):
        bar_with_ci(
            rate_by(arm_df, "cell", "differential_deception").reindex(
                [c for c in CELL_ORDER if c in set(arm_df["cell"].dropna())]
            ),
            f"differential deception by cell — arm {arm} (all models pooled)",
            OUT_DIR / f"deception_by_cell_{arm}.png",
        )
        bar_with_ci(
            rate_by(arm_df, "model", "differential_deception"),
            f"differential deception by model — arm {arm}",
            OUT_DIR / f"deception_by_model_{arm}.png",
        )
        bar_with_ci(
            rate_by(arm_df, "model", "other_fidelity"),
            f"other-model report fidelity (control) — arm {arm}",
            OUT_DIR / f"other_fidelity_by_model_{arm}.png",
        )


if __name__ == "__main__":
    main()
