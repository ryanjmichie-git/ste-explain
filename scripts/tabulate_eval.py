#!/usr/bin/env python3
"""Tabulate one eval iteration: per-assertion pass/fail, points, lint errors.

Layout: workspace/iteration-N/<eval>/<arm>/run-K/{output.md,grading.json}.
<arm> is with_skill for a single-arm eval, or arm-a, arm-b, ... for a paired
batch. One letter per assertion row: P pass (a JSON true), F fail. A grading
file that does not have exactly 5 rows is flagged with "!" and only its first
5 rows count. Points count every run present, so name supplementary runs when
you report.

Usage: python3 scripts/tabulate_eval.py workspace/iteration-N
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ste_lint import lint_text  # noqa: E402

PROCEDURE_EVALS = {"strict-bike-chain", "etl-runbook"}
EVAL_ORDER = [
    "oauth-simple",
    "rewrite-dense",
    "strict-bike-chain",
    "etl-runbook",
    "jargon-translation",
]


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    root = Path(sys.argv[1])
    totals = {}
    for ev in EVAL_ORDER:
        arms = sorted(
            p for p in (root / ev).glob("*") if p.is_dir() and p.name != "baseline"
        )
        for arm in arms:
            runs = sorted(arm.glob("run-*"), key=lambda p: int(p.name.split("-")[1]))
            marks, lint, pts = [], [], 0
            for run in runs:
                out = run / "output.md"
                if not out.exists():
                    marks.append("no-output")
                    lint.append("-")
                    continue
                errors, _ = lint_text(
                    out.read_text(encoding="utf-8"), procedure=ev in PROCEDURE_EVALS
                )
                lint.append(str(len(errors)))
                grading = run / "grading.json"
                if not grading.exists():
                    marks.append("ungraded")
                    continue
                rows = json.loads(grading.read_text(encoding="utf-8"))["expectations"]
                flag = "" if len(rows) == 5 else "!"
                rows = rows[:5]
                marks.append(
                    "".join("P" if r["passed"] is True else "F" for r in rows) + flag
                )
                pts += sum(r["passed"] is True for r in rows)
            if marks:
                print(
                    f"{ev:20s} {arm.name:11s} {pts:>3}  {' '.join(marks)}  "
                    f"lint {'/'.join(lint)}"
                )
                totals[arm.name] = totals.get(arm.name, 0) + pts
    for arm, pts in sorted(totals.items()):
        print(f"TOTAL {arm}: {pts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
