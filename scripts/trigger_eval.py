#!/usr/bin/env python3
"""Measure whether the skill triggers, using headless Claude Code sessions.

For each query in evals/trigger-evals.json, runs `claude -p` from an empty
temp dir with this repo loaded via --plugin-dir and only project settings
(so the user's own plugins do not compete). A run counts as triggered if
the session calls the Skill tool with ste-explain at any point.

Usage: python3 scripts/trigger_eval.py [--runs 3] [--max-turns 6] [--workers 4]

Use at least 6 turns: with fewer, a query that points at a file can end on
the file search before the model decides on the skill.

Writes workspace/trigger-results.jsonl. Exit codes: 0 every run meets the
success criteria (>=9/10 should-trigger, <=1/10 should-not), 1 otherwise.
"""

import argparse
import json
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
QUERIES = REPO / "evals" / "trigger-evals.json"
OUT = REPO / "workspace" / "trigger-results.jsonl"


def run_one(query, max_turns, cwd):
    cmd = [
        "claude",
        "-p",
        query,
        "--plugin-dir",
        str(REPO),
        "--setting-sources",
        "project",
        "--output-format",
        "stream-json",
        "--verbose",
        "--max-turns",
        str(max_turns),
        "--no-session-persistence",
    ]
    p = subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", timeout=600
    )
    skills = []
    for line in p.stdout.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("type") == "assistant":
            for block in event["message"]["content"]:
                if block.get("type") == "tool_use" and block["name"] == "Skill":
                    skills.append(block["input"].get("skill") or "")
    return {
        "triggered": any("ste-explain" in s for s in skills),
        "skills": skills,
        "rc": p.returncode,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--max-turns", type=int, default=6)
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()

    queries = json.loads(QUERIES.read_text(encoding="utf-8"))
    jobs = [(r, q) for r in range(args.runs) for q in queries]
    with tempfile.TemporaryDirectory() as cwd, ThreadPoolExecutor(args.workers) as ex:
        results = list(
            ex.map(lambda job: run_one(job[1]["query"], args.max_turns, cwd), jobs)
        )

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w", encoding="utf-8") as f:
        for (r, q), res in zip(jobs, results):
            f.write(json.dumps({"run": r, **q, **res}) + "\n")

    ok = True
    for r in range(args.runs):
        rows = [(q, res) for (rr, q), res in zip(jobs, results) if rr == r]
        pos = sum(res["triggered"] for q, res in rows if q["should_trigger"])
        neg = sum(res["triggered"] for q, res in rows if not q["should_trigger"])
        n_pos = sum(q["should_trigger"] for q, _ in rows)
        passed = pos >= 0.9 * n_pos and neg <= 0.1 * (len(rows) - n_pos)
        ok &= passed
        print(
            f"run {r + 1}: should-trigger {pos}/{n_pos}, should-not triggered {neg}/{len(rows) - n_pos}"
            f"  {'PASS' if passed else 'FAIL'}"
        )

    misses = [
        (q["query"], res["triggered"])
        for (_, q), res in zip(jobs, results)
        if res["triggered"] != q["should_trigger"]
    ]
    for query, triggered in misses:
        label = "false trigger" if triggered else "missed"
        print(f"  {label}: {query.splitlines()[0][:80]}")
    print(f"wrote {OUT.relative_to(REPO)}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
