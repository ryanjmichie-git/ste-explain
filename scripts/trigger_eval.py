#!/usr/bin/env python3
"""Measure whether the skill triggers, using headless Claude Code sessions.

For each query, runs `claude -p` from an empty temp dir with a copy of this
plugin loaded via --plugin-dir and only project settings (so the user's own
plugins do not compete). A run counts as triggered if the session calls the
Skill tool with this plugin's ste-explain skill at any point.

The plugin is always copied to a neutral temp dir first. A plugin path that
contains "ste-explain" leaks into the model's behavior and inflates results.

Usage:
  python3 scripts/trigger_eval.py [--runs 3] [--max-turns 6] [--workers 4]
      [--queries evals/trigger-evals.json]
      [--out workspace/trigger-results.jsonl] [--ref GITREF] [--model MODEL]

--ref GITREF runs a paired comparison in one batch: "old" uses SKILL.md from
GITREF, "new" uses the working tree. Trigger rates drift from day to day
(the same description scored 26/30 one day and 22/30 the next), so judge a
description change only with --ref, never against an earlier run.

Use at least 6 turns: with fewer, a query that points at a file can end on
the file search before the model decides on the skill.

A session that produces no assistant message (a crash or a timeout) is
retried once and then left out of the counts.

Exit codes:
  0  pass. Without --ref: should-trigger >= 22/30 and false triggers <= 2/30,
     scaled to the query file. With --ref: "new" is at most 2 should-trigger
     hits below "old" and has at most 1 more false trigger.
  1  fail.
  2  invalid run: another ste-explain copy was loaded, or more than 5% of the
     sessions failed.
"""

import argparse
import json
import os
import shutil
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILL_REL = "skills/ste-explain/SKILL.md"
OWN_SKILL = {"ste-explain:ste-explain", "ste-explain"}
TIMEOUT = 600


def make_plugin_copy(ref=None):
    """Copy the plugin to a neutral temp dir. With ref, take SKILL.md from that git ref."""
    root = Path(tempfile.mkdtemp()) / "plugin"
    shutil.copytree(REPO / ".claude-plugin", root / ".claude-plugin")
    shutil.copytree(REPO / "skills", root / "skills")
    if ref:
        old = subprocess.run(
            ["git", "show", f"{ref}:{SKILL_REL}"],
            cwd=REPO,
            capture_output=True,
            check=True,
        ).stdout
        (root / SKILL_REL).write_bytes(old)
    return root


def description(plugin_dir):
    text = (plugin_dir / SKILL_REL).read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.startswith("description:"):
            return line[len("description:") :].strip()
    return ""


def run_claude(cmd, cwd):
    p = subprocess.Popen(
        cmd,
        cwd=cwd,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    try:
        out, _ = p.communicate(timeout=TIMEOUT)
        return p.returncode, out
    except subprocess.TimeoutExpired:
        # On Windows, kill() leaves child processes that hold the pipe open.
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(p.pid)], capture_output=True
            )
        else:
            p.kill()
        try:
            out, _ = p.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            out = ""
        return "timeout", out


def run_one(query, plugin_dir, max_turns, cwd, model):
    cmd = [
        "claude",
        "-p",
        query,
        "--plugin-dir",
        str(plugin_dir),
        "--setting-sources",
        "project",
        "--output-format",
        "stream-json",
        "--verbose",
        "--max-turns",
        str(max_turns),
        "--no-session-persistence",
    ]
    if model:
        cmd += ["--model", model]
    res = {}
    for _ in range(2):  # one retry for a session that produced nothing
        skills, loaded, reply, used_model, n_assistant = [], [], "", "", 0
        try:
            rc, out = run_claude(cmd, cwd)
            for line in out.splitlines():
                try:
                    event = json.loads(line)
                except ValueError:
                    continue
                if not isinstance(event, dict):
                    continue
                if event.get("type") == "system" and event.get("subtype") == "init":
                    loaded = [s for s in event.get("skills", []) if "ste-explain" in s]
                    used_model = event.get("model") or ""
                if event.get("type") == "assistant":
                    n_assistant += 1
                    for block in event["message"]["content"]:
                        if block.get("type") == "tool_use" and block["name"] == "Skill":
                            skills.append(block["input"].get("skill") or "")
                if event.get("type") == "result":
                    reply = (event.get("result") or "")[:300]
        except (OSError, KeyError, TypeError) as e:
            rc = f"error: {e!r}"
        res = {
            "triggered": any(s in OWN_SKILL for s in skills),
            "valid": n_assistant > 0,
            "skills": skills,
            "loaded": loaded,
            "model": used_model,
            "reply": reply,
            "rc": rc,
        }
        if res["valid"]:
            break
    return res


def counts(rows):
    rows = [r for r in rows if r["valid"]]
    pos = sum(r["triggered"] for r in rows if r["should_trigger"])
    n_pos = sum(1 for r in rows if r["should_trigger"])
    neg = sum(r["triggered"] for r in rows if not r["should_trigger"])
    return pos, n_pos, neg, len(rows) - n_pos


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--max-turns", type=int, default=6)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--queries", default=str(REPO / "evals" / "trigger-evals.json"))
    ap.add_argument("--out", default=str(REPO / "workspace" / "trigger-results.jsonl"))
    ap.add_argument(
        "--ref", help="git ref of the old SKILL.md; runs old and new paired"
    )
    ap.add_argument("--model", help="passed to claude -p; default is the CLI default")
    args = ap.parse_args()

    queries = json.loads(Path(args.queries).read_text(encoding="utf-8"))
    variants = {"new": make_plugin_copy()}
    if args.ref:
        variants["old"] = make_plugin_copy(args.ref)
    for v in sorted(variants):
        print(f"{v} description: {description(variants[v])}")
    cwd = tempfile.mkdtemp()
    jobs = [(r, v, q) for r in range(args.runs) for q in queries for v in variants]

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    with ThreadPoolExecutor(args.workers) as ex, out.open("w", encoding="utf-8") as f:
        results = ex.map(
            lambda j: run_one(
                j[2]["query"], variants[j[1]], args.max_turns, cwd, args.model
            ),
            jobs,
        )
        for (r, v, q), res in zip(jobs, results):
            row = {"run": r, "variant": v, **q, **res}
            rows.append(row)
            f.write(json.dumps(row) + "\n")
            f.flush()
    for d in variants.values():
        shutil.rmtree(d.parent, ignore_errors=True)
    shutil.rmtree(cwd, ignore_errors=True)

    print()
    for v in sorted(variants):
        for r in range(args.runs):
            pos, n_pos, neg, n_neg = counts(
                [x for x in rows if x["variant"] == v and x["run"] == r]
            )
            print(
                f"{v} run {r + 1}: should-trigger {pos}/{n_pos}, "
                f"should-not triggered {neg}/{n_neg}"
            )
    total = {v: counts([x for x in rows if x["variant"] == v]) for v in variants}
    for v in sorted(variants):
        pos, n_pos, neg, n_neg = total[v]
        print(
            f"{v} total: should-trigger {pos}/{n_pos}, should-not triggered {neg}/{n_neg}"
        )
    print()
    for q in queries:
        cells = []
        for v in sorted(variants):
            mine = [
                x
                for x in rows
                if x["variant"] == v and x["query"] == q["query"] and x["valid"]
            ]
            cells.append(f"{v} {sum(x['triggered'] for x in mine)}/{len(mine)}")
        mark = "T" if q["should_trigger"] else "N"
        print(f"{mark} {'  '.join(cells)}  {q['query'].splitlines()[0][:70]}")

    invalid = [x for x in rows if not x["valid"]]
    models = sorted({x["model"] for x in rows if x["model"]})
    print(f"\nmodel(s): {', '.join(models) or 'not reported'}")
    print(f"invalid sessions (left out): {len(invalid)}/{len(rows)}")
    print(f"wrote {out}")
    others = {s for x in rows for s in x["loaded"] if s not in OWN_SKILL}
    if others:
        print(f"INVALID RUN: other ste-explain copies loaded: {sorted(others)}")
        return 2
    if len(invalid) > 0.05 * len(rows):
        print("INVALID RUN: more than 5% of the sessions failed")
        return 2
    pos, n_pos, neg, n_neg = total["new"]
    if args.ref:
        old_pos, _, old_neg, _ = total["old"]
        ok = pos >= old_pos - 2 and neg <= old_neg + 1
    else:
        ok = pos * 30 >= 22 * n_pos and neg * 30 <= 2 * n_neg
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
