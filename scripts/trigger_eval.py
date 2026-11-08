#!/usr/bin/env python3
"""Measure whether the skill triggers, using headless Claude Code sessions.

For each query, runs `claude -p` from its own empty temp dir with a copy of
this plugin loaded via --plugin-dir and only project settings (so the user's
own plugins do not compete). A run counts as triggered if the session calls
the Skill tool with this plugin's ste-explain skill at any point.

The plugin is always copied to a neutral temp dir first. A plugin path that
contains "ste-explain" leaks into the model's behavior and inflates results.

Isolation. Every session gets the switches that keep the user's CLAUDE.md,
auto memory, synced claude.ai skills, MCP servers and Chrome out, and none of
the parent's CLAUDE* environment variables (a session started from inside
Claude Code inherits CLAUDECODE, CLAUDE_EFFORT and more). With --token-file
(a token from `claude setup-token`), every session also gets its own empty
CLAUDE_CONFIG_DIR, so no user state at all, usage counts included, reaches it.
A session whose init event shows another ste-explain copy, a synced skill, an
MCP server, another model than --model, or other skills or plugins than the
first session of its variant stops the batch at once (exit 2).

Usage:
  python3 scripts/trigger_eval.py [--runs 3] [--max-turns 6] [--workers 4]
      [--queries evals/trigger-evals.json]
      [--out workspace/trigger-results.jsonl] [--ref GITREF] [--model MODEL]
      [--token-file PATH]

--ref GITREF runs a paired comparison in one batch: "old" uses SKILL.md from
GITREF, "new" uses the working tree. Trigger rates drift from day to day
(the same description scored 26/30 one day and 22/30 the next), so judge a
description change only with --ref, never against an earlier run.

Use at least 6 turns: with fewer, a query that points at a file can end on
the file search before the model decides on the skill.

A session fails if it produces no assistant message, if it times out or its
stream breaks, or if it ends on an error result (a usage limit, for example;
running out of turns is a real end), unless the skill call came first. A
failed session is retried once and then left out of the counts. With --ref,
the same run of the same query is then left out of both variants. Run 1
starts each query with "new", run 2 with "old", and so on.

Exit codes:
  0  pass. Without --ref: should-trigger >= 22/30 and false triggers <= 2/30,
     scaled to the query file. With --ref: "new" is at most 2 should-trigger
     hits below "old" and has at most 1 more false trigger.
  1  fail.
  2  invalid run: a contaminated session (see Isolation), more than 5% of the
     sessions failed, or the script itself failed (a bad --ref, for example).
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import types
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILL_REL = "skills/ste-explain/SKILL.md"
OWN_SKILL = {"ste-explain:ste-explain", "ste-explain"}
TIMEOUT = 600
ISOLATION_ENV = {
    "CLAUDE_CODE_DISABLE_CLAUDE_MDS": "1",
    "CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1",
    "ENABLE_CLAUDEAI_MCP_SERVERS": "false",
}


def make_plugin_copy(ref=None):
    """Copy the plugin to a neutral temp dir. With ref, take SKILL.md from that git ref."""
    tmp = Path(tempfile.mkdtemp())
    root = tmp / "plugin"
    try:
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
    except Exception:
        shutil.rmtree(tmp, ignore_errors=True)
        raise
    return root


def description(plugin_dir):
    text = (plugin_dir / SKILL_REL).read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.startswith("description:"):
            return line[len("description:") :].strip()
    return ""


def session_env(token, config_dir):
    """The parent env without its CLAUDE* session variables, plus the switches."""
    env = {
        k: v
        for k, v in os.environ.items()
        if not k.upper().startswith("CLAUDE") or k.upper() == "CLAUDE_CONFIG_DIR"
    }
    env.update(ISOLATION_ENV)
    if token:
        env["CLAUDE_CONFIG_DIR"] = config_dir
        env["CLAUDE_CODE_OAUTH_TOKEN"] = token
    return env


def norm(path):
    return os.path.normcase(os.path.realpath(path))


def contamination(init, plugin_dir, batch):
    """Return why this init event shows a session that is not clean, or ""."""
    plugins = init.get("plugins") or []
    own = [p for p in plugins if str(p.get("name", "")).split("@")[0] == "ste-explain"]
    if len(own) != 1 or norm(own[0].get("path", "")) != norm(plugin_dir):
        return f"ste-explain plugins {own}"
    skills = init.get("skills") or []
    synced = [s for s in skills if s.startswith("anthropic-skills:")]
    if synced:
        return f"synced claude.ai skills {synced}"
    if init.get("mcp_servers"):
        return f"MCP servers {init['mcp_servers']}"
    if batch.model and init.get("model") != batch.model:
        return f"model {init.get('model')!r}, not {batch.model!r}"
    snap = (
        sorted(skills),
        sorted(norm(p.get("path", "")) for p in plugins),
        init.get("model"),
    )
    with batch.lock:
        first = batch.snapshots.setdefault(norm(plugin_dir), snap)
    if snap != first:
        return "skills, plugins or model differ from the first session"
    return ""


def run_claude(cmd, cwd, env):
    p = subprocess.Popen(
        cmd,
        cwd=cwd,
        env=env,
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


def session(cmd, cwd, env, plugin_dir, batch):
    """Run one session and read its stream."""
    skills, loaded, reply, n_assistant = [], [], "", 0
    init, result, contaminated = {}, {}, ""
    try:
        rc, out = run_claude(cmd, cwd, env)
        for line in out.splitlines():
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if not isinstance(event, dict):
                continue
            if event.get("type") == "system" and event.get("subtype") == "init":
                init = event
                loaded = [s for s in event.get("skills", []) if "ste-explain" in s]
                contaminated = contamination(event, plugin_dir, batch)
            if event.get("type") == "assistant":
                n_assistant += 1
                for block in event["message"]["content"]:
                    if block.get("type") == "tool_use" and block["name"] == "Skill":
                        skills.append(block["input"].get("skill") or "")
            if event.get("type") == "result":
                result = event
                reply = (event.get("result") or "")[:300]
    except (OSError, KeyError, TypeError, AttributeError) as e:
        rc = f"error: {e!r}"
    triggered = any(s in OWN_SKILL for s in skills)
    # A string rc is a timeout or a broken stream. An error result is a usage
    # limit or an API error; running out of turns is a real end. Such a
    # session counts only if the skill call came first.
    failed = isinstance(rc, str) or (
        bool(result.get("is_error")) and result.get("subtype") != "error_max_turns"
    )
    return {
        "triggered": triggered,
        "valid": n_assistant > 0 and not contaminated and (triggered or not failed),
        "contaminated": contaminated,
        "skills": skills,
        "loaded": loaded,
        "plugins": init.get("plugins") or [],
        "model": init.get("model") or "",
        "version": init.get("claude_code_version") or "",
        "subtype": result.get("subtype") or "",
        "is_error": bool(result.get("is_error")),
        "reply": reply,
        "rc": rc,
    }


def run_one(query, plugin_dir, batch):
    cmd = [
        "claude",
        "-p",
        query,
        "--plugin-dir",
        str(plugin_dir),
        "--setting-sources",
        "project",
        "--settings",
        str(batch.settings),
        "--strict-mcp-config",
        "--no-chrome",
        "--output-format",
        "stream-json",
        "--verbose",
        "--max-turns",
        str(batch.max_turns),
        "--no-session-persistence",
    ]
    if batch.model:
        cmd += ["--model", batch.model]
    res = None
    for _ in range(2):  # one retry for a session that produced nothing
        if batch.stop.is_set():
            break
        cwd = tempfile.mkdtemp()
        config = tempfile.mkdtemp() if batch.token else None
        try:
            res = session(
                cmd, cwd, session_env(batch.token, config), plugin_dir, batch
            )
        finally:
            shutil.rmtree(cwd, ignore_errors=True)
            if config:
                shutil.rmtree(config, ignore_errors=True)
        if res["contaminated"]:
            batch.stop.set()
            break
        if res["valid"]:
            break
    if res is None:  # the batch stopped before this session started
        res = {
            "triggered": False,
            "valid": False,
            "contaminated": "",
            "skills": [],
            "loaded": [],
            "plugins": [],
            "model": "",
            "version": "",
            "subtype": "",
            "is_error": False,
            "reply": "",
            "rc": "skipped",
        }
    return res


def counts(rows):
    rows = [r for r in rows if r["valid"]]
    pos = sum(r["triggered"] for r in rows if r["should_trigger"])
    n_pos = sum(1 for r in rows if r["should_trigger"])
    neg = sum(r["triggered"] for r in rows if not r["should_trigger"])
    return pos, n_pos, neg, len(rows) - n_pos


def both_valid(rows):
    """Keep a (run, query) only if its session is valid in every variant."""
    bad = {(r["run"], r["query"]) for r in rows if not r["valid"]}
    return [r for r in rows if (r["run"], r["query"]) not in bad]


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
    ap.add_argument(
        "--token-file",
        help="file with a `claude setup-token` token; each session then gets "
        "its own empty CLAUDE_CONFIG_DIR",
    )
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        # A redirected stdout on Windows is cp1252. A query can hold more.
        sys.stdout.reconfigure(errors="backslashreplace")
    tmp = []
    try:
        return run(args, tmp)
    except Exception as e:
        # Not exit 1: a caller reads 1 as "the new description costs triggers".
        print(f"INVALID RUN: {e!r}")
        return 2
    finally:
        for d in tmp:
            shutil.rmtree(d, ignore_errors=True)


def run(args, tmp):
    """Run the batch and return the exit code. Temp dirs go into tmp for cleanup."""
    queries = json.loads(Path(args.queries).read_text(encoding="utf-8"))
    variants = {"new": make_plugin_copy()}
    tmp.append(variants["new"].parent)
    if args.ref:
        variants["old"] = make_plugin_copy(args.ref)
        tmp.append(variants["old"].parent)
    for v in sorted(variants):
        print(f"{v} description: {description(variants[v])}")
    token = ""
    if args.token_file:
        token = Path(args.token_file).read_text(encoding="utf-8").strip()
    settings_dir = tempfile.mkdtemp()
    tmp.append(settings_dir)
    settings = Path(settings_dir) / "settings.json"
    settings.write_text(json.dumps({"syncClaudeAiSkills": False}), encoding="utf-8")
    batch = types.SimpleNamespace(
        max_turns=args.max_turns,
        model=args.model,
        token=token,
        settings=settings,
        lock=threading.Lock(),
        snapshots={},
        stop=threading.Event(),
    )
    order = list(variants)
    jobs = [
        (r, v, q)
        for r in range(args.runs)
        for q in queries
        for v in (order if r % 2 == 0 else order[::-1])
    ]

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    with ThreadPoolExecutor(args.workers) as ex, out.open("w", encoding="utf-8") as f:
        results = ex.map(lambda j: run_one(j[2]["query"], variants[j[1]], batch), jobs)
        for (r, v, q), res in zip(jobs, results):
            row = {"run": r, "variant": v, **q, **res}
            rows.append(row)
            f.write(json.dumps(row) + "\n")
            f.flush()
    kept = both_valid(rows)

    print()
    for v in sorted(variants):
        for r in range(args.runs):
            pos, n_pos, neg, n_neg = counts(
                [x for x in kept if x["variant"] == v and x["run"] == r]
            )
            print(
                f"{v} run {r + 1}: should-trigger {pos}/{n_pos}, "
                f"should-not triggered {neg}/{n_neg}"
            )
    total = {v: counts([x for x in kept if x["variant"] == v]) for v in variants}
    for v in sorted(variants):
        pos, n_pos, neg, n_neg = total[v]
        print(
            f"{v} total: should-trigger {pos}/{n_pos}, should-not triggered {neg}/{n_neg}"
        )
    print()
    for q in queries:
        cells = []
        for v in sorted(variants):
            mine = [x for x in kept if x["variant"] == v and x["query"] == q["query"]]
            cells.append(f"{v} {sum(x['triggered'] for x in mine)}/{len(mine)}")
        mark = "T" if q["should_trigger"] else "N"
        print(f"{mark} {'  '.join(cells)}  {q['query'].splitlines()[0][:70]}")

    invalid = [x for x in rows if not x["valid"]]
    models = sorted({x["model"] for x in rows if x["model"]})
    versions = sorted({x["version"] for x in rows if x["version"]})
    print(f"\nmodel(s): {', '.join(models) or 'not reported'}")
    print(f"Claude Code version(s): {', '.join(versions) or 'not reported'}")
    print(f"invalid sessions (left out): {len(invalid)}/{len(rows)}")
    print(f"wrote {out}")
    bad = [x for x in rows if x["contaminated"]]
    if bad:
        x = bad[0]
        print(
            f"INVALID RUN: contaminated session ({x['variant']}, "
            f"{x['query'].splitlines()[0][:40]!r}): {x['contaminated']}"
        )
        return 2
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
