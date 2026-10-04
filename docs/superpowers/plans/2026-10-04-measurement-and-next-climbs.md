# Measurement Hardening and Next Climbs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task, inline in one session. Do NOT use subagent-driven-development: Tasks 4 to 6 orchestrate subagents themselves, and subagents cannot spawn subagents. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make ste-explain edits measurable (paired runs, pinned grading, a fair linter and trigger script), then use that to settle the jargon-timing failure, the rewrite fact 7 failure, and the reverted hygiene bundle.

**Architecture:** Three tooling tasks land first and are committed (linter, trigger script, grading standards and criteria). Then one screen (iteration-14) tests candidate skill edits on the two cheap evals with 6 runs per arm, one paired confirm (iteration-15) tests the winner and the hygiene bundle against the committed text in the same session, and one status batch (iteration-16) measures the final text.

**Tech Stack:** Python 3 standard library only (`python` on this Windows machine, not `python3`), Git Bash, the repo's subagents (`skill-tester`, `grader`, `red-team-reviewer`, plus `general-purpose` for screen graders), headless `claude -p` for trigger runs.

**Spec:** `specs/skill-spec.md` (contract), `specs/success-criteria.md` (rewritten in Task 3), `CLAUDE.md` (dev rules), `docs/hillclimb-log.md`, and `workspace/iteration-10/summary.md` to `workspace/iteration-13/summary.md` (evidence for everything below; gitignored but present on disk).

## Context

The last session ran three climbs (2026-10-04). Rule 11 was kept (commit 658edb6, plugin 0.1.4): verb-first passes went from 16 of 30 procedure runs to 16 of 18. A rule 12 rewrite and a hygiene bundle were reverted. What it left open:

1. **Jargon assertion 5 fails 3/3 in every iteration since 9.** The output never says that copies match only when no new changes arrive, or it states a time bound ("within seconds"). Only iteration-8 fixed it (3/3), with the sentence "Do not make a claim stronger to make it simpler."
2. **Rewrite fact 7 fails about 1 run in 4.** Source: "is anticipated to require board approval in the second quarter". Pass: "The agency expects the purchase to need board approval in the second quarter". Fail: "will probably need". Any rule-12 sentence telling the model to keep limits or qualifiers (iterations 3, 8, 10) raised failure to 2/3 or 3/3. Never put such a sentence in rule 12 again.
3. **One batch is noise.** The same text drew 72/75 then 68/75. The same description triggered 26/30 one day and 22/30 the next. Graders drifted (one rejected "While you hold the brake lever, push ..." that six iterations accepted). So every decision in this plan is made inside one batch against a control arm.
4. **The linter over-counts.** `--procedure` applies 20 words to notes and intro prose, and counts the "Note:" label.
5. **The hygiene bundle is unresolved.** It scored 41/45 and 42/45 on three evals against one 45/45 draw of the committed text, with no mechanism. It is saved as `workspace/iteration-12/hygiene-bundle.patch`.

### Decisions embedded in this plan (the user approves them by approving the plan)

- **Keep rule changes.** "Total must improve" becomes: the edit's target assertion improves, pooled over screen and confirm, and the edited arm's total is at most 3 below the control arm in the same batch.
- **Success criteria** become rates over 6 runs and a 22/30 trigger floor (Task 3, full text below).
- **Verb-first standard is pinned:** a step may open with one condition or time clause (If, When, While, Before, After, Until) followed by a command in the same sentence.
- **Hygiene rule:** apply the bundle unless its arm is 3 or more points below the control arm in the same batch.
- **Push:** approved by the user on 2026-10-04 ("go with your suggestions"). Private repo `ryanjmichie-git/ste-explain`.

## Global Constraints

- Work in the main checkout on branch `main`. Do not create a worktree or a feature branch, even though superpowers:executing-plans asks for one: the steps read gitignored files under `workspace/` that exist only in the main checkout, and this repo commits to `main`. The user approved this with the plan on 2026-10-04. For the final review that executing-plans runs, MERGE_BASE is HEAD as it stands at the end of Task 0.
- Never copy text from the ASD-STE100 PDF. The skill ships with zero scripts and zero dependencies; nothing in `scripts/` may be referenced from SKILL.md.
- Frontmatter: name ≤64 chars `[a-z0-9-]`; description ≤1024 chars, single line; SKILL.md body ≤150 lines; `references/rules.md` ≤200 lines. Edits to SKILL.md with the Edit tool trigger a validation hook; a `git apply` does not, so run `python scripts/validate_skill.py` after every apply.
- The skill's own prose must pass `python scripts/ste_lint.py skills/ste-explain/SKILL.md` with 0 errors (paragraphs ≤6 sentences, sentences ≤25 words).
- Testers, graders and reviewers are subagents. Never write or grade an eval answer in the main session.
- `skill-tester` reads the fixed path `skills/ste-explain/SKILL.md`. Never change files under `skills/` while any tester is running.
- Never give a tester `evals/fixtures/dense-paragraph.md`. It holds the grader's fact list. Testers get `workspace/iteration-N/rewrite-dense/input.md` (the paragraph only).
- Never commit an arm. Only a kept edit is committed, with a `.claude-plugin/plugin.json` version bump (0.1.5, 0.1.6, ...) and a row in `docs/hillclimb-log.md` (newest first, same columns as existing rows).
- Commit subjects: `feat:`, `fix:`, `docs:`, `eval:`, `spec:`. End every commit message with `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`.
- `workspace/` and `dist/` are gitignored and disposable. Durable results go in `docs/hillclimb-log.md`.
- Report usage as counts of subagent runs and headless sessions plus token totals from task notifications. The user reads the plan-window percentage from `/usage`.
- Do not pause for approval between tasks. STOP and report only when a STOP line in a task fires, a git state is not what the step expects, or a kept edit would violate `specs/skill-spec.md`.
- If the session restarts mid-wave, list the output files on disk, relaunch only the missing testers or graders, and continue. Outputs on disk are the source of truth.

## File map

| File | Action | Responsibility |
| --- | --- | --- |
| `scripts/ste_lint.py` | modify | per-sentence limits in `--procedure`; labels not counted |
| `scripts/trigger_eval.py` | rewrite | neutral plugin copies, `--queries`, `--out`, `--ref` pairing, `--model`, failed-session handling |
| `evals/trigger-heldout.json` | create | 16 held-out trigger queries |
| `evals/trigger-evals.json` | modify | context for the ETL and fare-validation queries |
| `evals/evals.json` | modify | `grading_notes` per eval (pinned standards) |
| `.claude/agents/grader.md` | modify | 5 rows + `quality` key; apply `grading_notes` |
| `scripts/tabulate_eval.py` | create | per-arm table of grades and lint errors |
| `scripts/screen_blind.py` | create | blind copies and majority tally for the screen |
| `.claude/commands/eval.md`, `.claude/commands/hillclimb.md` | modify | 3 runs, waves, paired keep rule |
| `CLAUDE.md` | modify | commands and the paired-run rule |
| `specs/success-criteria.md` | rewrite | rates over 6 runs; trigger floor |
| `skills/ste-explain/SKILL.md`, `references/rules.md` | modify only if an arm is kept | the product |

## Standing procedures (used by Tasks 4 to 6)

**P1. Tester prompt** (subagent_type `skill-tester`, run in background, launch a whole wave in one message):

```
Eval prompt (answer exactly this, as a fresh user session with the ste-explain skill installed):

<PROMPT>

Input files: <none. | workspace/iteration-N/rewrite-dense/input.md (the paragraph to rewrite).>
Output path: workspace/iteration-N/<eval>/<arm>/run-K/output.md (write ONLY the final answer there).
```

`<PROMPT>` is the eval's `prompt` from `evals/evals.json`, verbatim, except for rewrite-dense, where it is `rewrite this paragraph so it's easier to read (file: workspace/iteration-N/rewrite-dense/input.md)`. Create `input.md` with `cp workspace/iteration-13/rewrite-dense/input.md workspace/iteration-N/rewrite-dense/input.md`; it must be exactly 14 lines starting "In consideration of the fact". If that file is gone, copy lines 8 to 21 of `evals/fixtures/dense-paragraph.md`.

**P2. Standard grader prompt** (subagent_type `grader`, one per output, background):

```
Grade this eval output.

Eval: <eval name> (eval id <id> in evals/evals.json; <"description mode, so run the linter WITHOUT --procedure" | "procedure, so run the linter WITH --procedure: `python scripts/ste_lint.py --procedure <file>`">).
Output file: <path to output.md>
<rewrite-dense only:> Source paragraph the tester was given: workspace/iteration-N/rewrite-dense/input.md
<rewrite-dense only:> Grader's fact list (8 facts plus the certainty rule): evals/fixtures/dense-paragraph.md, section "Fact list (grader only)".

Assertions (verbatim from evals/evals.json):
1. ...
2. ...
3. ...
4. ...
5. ...

Grading notes (the standing reading of each assertion; apply them and do not read gradings from other iterations or skills/ste-explain/SKILL.md to calibrate):
<the eval's grading_notes, one per line>

Write grading.json next to the output file with exactly these 5 assertions as the 5 rows of "expectations", in this order. Put your quality judgment (correct, complete, natural) in a separate top-level key "quality": {"passed": true/false, "evidence": "..."} rather than as a 6th row.

Report back: eval name, pass count / 5, and the one most important failure if any.
```

Procedure evals are strict-bike-chain (id 3) and etl-runbook (id 4). The others are description mode.

**P3. Wave.** One wave runs one arm.

1. `git status --short` prints nothing. If it prints anything, STOP.
2. For a non-control arm: `git apply <patch>` then `python scripts/validate_skill.py && python scripts/ste_lint.py skills/ste-explain/SKILL.md | tail -1` (must say `ok:` and `0 error(s)`).
3. Append a line to `workspace/iteration-N/waves.md`: wave number, arm, runs, and the output of `git hash-object skills/ste-explain/SKILL.md`.
4. Launch all testers of the wave in ONE message (P1).
5. Wait until every `output.md` of the wave exists (`ls`). Relaunch a tester that finished without writing its file, at most twice per run; a third failure is a STOP.
6. For a non-control arm: `git apply -R <patch>`. Then `git status --short` must print nothing. Only then start the next wave.

**P4. Red-team prompt** (subagent_type `red-team-reviewer`, background, launched while its arm's patch is applied):

```
Fresh-eyes adversarial review of the ste-explain skill as it stands now: `skills/ste-explain/SKILL.md` and `skills/ste-explain/references/rules.md`. Follow your standard review order.

The change under review, relative to the committed version:

<paste `git diff -- skills/`>

Context: two failures drive this change. (1) Explanations state a claim more strongly than the facts ("all copies will agree within seconds"). (2) Rewrites turn "is anticipated to require" into "will probably need". Three earlier wordings that told the model to keep limits or qualifiers made (2) worse. Judge whether this wording avoids that, whether it echoes any eval topic in evals/evals.json, and whether the skill's own prose still obeys its rules.

Report: a verdict line (SOUND, MINOR ISSUES (n), or MAJOR ISSUES (n)) followed by numbered findings, each with the file:line and a one-line fix. Keep it under 350 words.
```

---

### Task 0: Preflight and push

**Files:** none modified.

- [ ] **Step 1: Read the context.** Read `CLAUDE.md`, `specs/skill-spec.md`, `specs/success-criteria.md`, `docs/hillclimb-log.md`, `workspace/iteration-13/summary.md`, `workspace/iteration-12/summary.md`, and the two project memory notes (`trigger-eval-method`, `eval-run-conventions`).

- [ ] **Step 2: Verify the starting state.**

Run: `git log --oneline -2 && git status --short && python scripts/validate_skill.py && python scripts/ste_lint.py --self-test`
Expected: top commit `6db40b4 eval: log hygiene bundle (iterations 12-13), reverted` (or a later `docs:` commit that adds this plan), second line `658edb6 ...`; status shows at most this plan file untracked; `ok: name='ste-explain', description 657 chars, body 64 lines`; `self-test PASS`.

- [ ] **Step 3: Commit this plan if it is an untracked file in the repo, then push.**

```bash
git add docs/superpowers/plans/ 2>/dev/null; git commit -q -m "docs: add measurement and next-climbs plan

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" || true
git push origin main
git rev-list --left-right --count origin/main...main
```
Expected: last line `0	0`.

---

### Task 1: Linter limits for notes and prose in procedures

**Files:**
- Modify: `scripts/ste_lint.py` (docstring lines 8-15, constants after line 175, `lint_text` lines 210-250, `self_test` before line 347, `--procedure` help line 356)
- Modify: `CLAUDE.md:9-10`, `.claude/commands/lint.md:5-6`

**Interfaces:**
- Produces: `lint_text(text, procedure=False) -> (errors, warnings)` with the same signature. In procedure mode a list item and the first sentence of a Warning/Caution take 20 words; a Note/Tip, later sentences of a warning, and non-list prose take 25. Text with no list at all takes 20 throughout. Labels are never counted. Description mode is unchanged.

- [ ] **Step 1: Write the failing tests.** In `self_test()`, insert this block directly above the line `print("self-test PASS")`:

```python
    # Procedure mode: a step and the command of a warning take 20 words. A
    # note, a reason after a warning command, and prose around a list take 25.
    s22 = (
        "Turn the handle of the chain tool slowly until the pin of the tool "
        "pushes the rivet fully out of the chain."
    )
    n25 = (
        "The new chain and its quick link must have the same number of links "
        "as the old chain before you removed it from the bicycle."
    )

    def errs(text, procedure=True):
        return lint_text(text, procedure=procedure)[0]

    assert any(
        "22-word sentence (limit 20)" in e for e in errs("1. Wear gloves.\n2. " + s22)
    ), "a 22-word step must be an error"
    assert not errs("1. Wear gloves.\n\n   **Note:** " + s22), "note after a blank line"
    assert not errs("1. Count the links.\n   Note: " + n25), "label counted as a word"
    wrapped_note = (
        "1. Count the links.\n   Note: The new chain and its quick link must "
        "have the same number\n   of links as the old chain before you removed "
        "it from the bicycle again."
    )
    assert any("26-word sentence (limit 25)" in e for e in errs(wrapped_note))
    assert any(
        "(limit 20)" in e for e in errs("**WARNING:** " + s22 + "\n\n1. Wear gloves.")
    ), "the command of a warning takes 20"
    own_unit = (
        "1. Remove the old chain from the rear derailleur\n"
        "   Note: You need the old chain later to count the number of links in it"
    )
    assert not errs(own_unit), "a note line must not merge into its step"
    assert not errs("> **NOTE:** " + s22 + "\n\n1. Wear gloves."), "blockquote note"
    lead_in = (
        "Before you start, make sure that you have all of the tools in this "
        "list and a clean place to work:\n- Chain tool\n- Gloves"
    )
    assert not errs(lead_in), "lead-in prose before a list is a description"
    assert not errs(
        "Warning: Wear gloves. " + s22 + "\n\n1. Remove the chain."
    ), "a reason after a warning command is a description"
    assert any("(limit 20)" in e for e in errs(s22)), "no list: all instructions"
    assert not errs("1. Wear gloves.\n2. " + s22, procedure=False)
```

- [ ] **Step 2: Run the self-test and see it fail.**

Run: `python scripts/ste_lint.py --self-test`
Expected: `AssertionError: note after a blank line` (the first new case that the old code fails).

- [ ] **Step 3: Implement.** Add two constants directly after the line `HEADING_RE = re.compile(r"^\s*#{1,6}\s+")`:

```python
LABEL_RE = re.compile(r"^(note|tip|warning|caution|important)\s*:\s*", re.IGNORECASE)
NOTE_LABELS = {"note", "tip"}
```

Then replace `lint_text` from its `def` line down to and including the line `for sent in sentences:` and its two following lines (`n = word_count(sent)` and `if n > limit:`) with this. Everything after `if n > limit:` (the `errors.append(...)` call, the passive, hedge, noun-cluster, semicolon and -ing checks, and `return errors, warnings`) stays as it is.

````python
def lint_text(text: str, procedure: bool = False):
    errors, warnings = [], []

    # YAML frontmatter, fenced code blocks, and table rows are exempt.
    text = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.DOTALL)
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text = "\n".join(l for l in text.splitlines() if not l.lstrip().startswith("|"))

    # --procedure: a step (list item) and the command sentence of a Warning
    # or Caution take the 20-word limit. A note, a reason after a warning
    # command, and prose around the list are descriptions and take 25. Text
    # with no list at all is treated as instructions throughout.
    has_list = any(BULLET_RE.match(l) for l in text.splitlines())

    paragraphs = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    for pi, para in enumerate(paragraphs, 1):
        lines = para.splitlines()
        if not lines:
            continue
        is_list = any(BULLET_RE.match(l) for l in lines)
        if HEADING_RE.match(lines[0]):
            continue
        # Each unit is [text, limit of its first sentence, limit of the rest].
        # In a list, each bullet starts a new unit, so a ":" lead-in or an
        # unpunctuated item does not merge with the next item. A labelled
        # line (Note:, Warning:) also starts a unit. Wrapped continuation
        # lines stay with their unit.
        units = []
        for l in lines:
            is_bullet = bool(BULLET_RE.match(l))
            seg = strip_markdown(BULLET_RE.sub("", l)).strip()
            seg = re.sub(r"^>\s*", "", seg)
            label = LABEL_RE.match(seg)
            if label:
                seg = seg[label.end() :]
            if not units or label or (is_list and is_bullet):
                if not procedure:
                    first = rest = DESCRIPTION_LIMIT
                elif label:
                    is_note = label.group(1).lower() in NOTE_LABELS
                    first = DESCRIPTION_LIMIT if is_note else PROCEDURE_LIMIT
                    rest = DESCRIPTION_LIMIT
                elif is_bullet or not has_list:
                    first = rest = PROCEDURE_LIMIT
                else:
                    first = rest = DESCRIPTION_LIMIT
                units.append([seg, first, rest])
            else:
                units[-1][0] += " " + seg
        clean = " ".join(u[0] for u in units)
        sentences = [
            (s, u[1] if i == 0 else u[2])
            for u in units
            for i, s in enumerate(split_sentences(u[0]))
        ]

        if not is_list and len(sentences) > PARAGRAPH_LIMIT:
            errors.append(
                f"para {pi}: {len(sentences)} sentences (limit {PARAGRAPH_LIMIT})"
            )

        for sent, limit in sentences:
            n = word_count(sent)
            if n > limit:
````

Also change the `--procedure` help string to `"20-word limit for steps and warnings, 25 for notes and prose"`, and in the module docstring replace the line `Errors: sentence over limit, paragraph over 6 sentences.` with:

```
Errors: sentence over limit, paragraph over 6 sentences. With --procedure,
steps and warning commands take 20 words; notes and prose take 25.
```

- [ ] **Step 4: Run the tests and the regression checks.**

Run: `python scripts/ste_lint.py --self-test`
Expected: `self-test PASS`

Run: `for f in workspace/iteration-11/strict-bike-chain/with_skill/run-2 workspace/iteration-11/strict-bike-chain/with_skill/run-3; do python scripts/ste_lint.py --procedure $f/output.md | tail -1; done; python scripts/ste_lint.py workspace/iteration-11/oauth-simple/with_skill/run-1/output.md | tail -1; python scripts/ste_lint.py skills/ste-explain/SKILL.md | tail -1`
Expected: the two bike files now report `0 error(s)` (each had 1 before); the oauth file `0 error(s), 10 warning(s)` (unchanged); SKILL.md `0 error(s), 17 warning(s)` (unchanged).

- [ ] **Step 5: Update the two docs that describe the flag.** In `CLAUDE.md` change `(\`--procedure\` for 20-word limit, \`--json\`, \`--self-test\`)` to `(\`--procedure\`: 20 words for steps and warnings, 25 for notes and prose; \`--json\`; \`--self-test\`)`. In `.claude/commands/lint.md` change `add \`--procedure\` if the file is instructions/steps` to `add \`--procedure\` if the file is instructions/steps: steps and warnings then take 20 words, notes and prose 25`.

- [ ] **Step 6: Commit.**

```bash
git add scripts/ste_lint.py CLAUDE.md .claude/commands/lint.md
git commit -q -m "eval: lint notes and prose in procedures at the description limit

--procedure applied 20 words to every sentence and counted the Note label.
The spec gives 20 words to instructions and 25 to descriptions.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 2: Paired trigger runs, held-out file, query context

**Files:**
- Rewrite: `scripts/trigger_eval.py`
- Create: `evals/trigger-heldout.json`
- Modify: `evals/trigger-evals.json:6` and `:11`

**Interfaces:**
- Produces: `python scripts/trigger_eval.py [--runs 3] [--max-turns 6] [--workers 4] [--queries PATH] [--out PATH] [--ref GITREF] [--model MODEL]`. Rows in the output JSONL gain `variant` ("new" or "old"), `valid`, `model`. Exit 0 pass, 1 fail, 2 invalid run.

- [ ] **Step 1: Replace `scripts/trigger_eval.py` with this file.**

```python
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
    ap.add_argument("--ref", help="git ref of the old SKILL.md; runs old and new paired")
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
        print(f"{v} total: should-trigger {pos}/{n_pos}, should-not triggered {neg}/{n_neg}")
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
```

- [ ] **Step 2: Create `evals/trigger-heldout.json`** (16 queries used in iteration-12; in no other eval file):

```json
[
  {"query": "I'm new to Rust, explain lifetimes", "should_trigger": true},
  {"query": "explain what a mortgage escrow account is in layman's terms", "should_trigger": true},
  {"query": "explain how vaccines train the immune system, I need to tell my grandma", "should_trigger": true},
  {"query": "our sales team keeps asking what Kubernetes is. give me an explanation they'd get", "should_trigger": true},
  {"query": "no jargon please: what does a CDN do?", "should_trigger": true},
  {"query": "summarize this for my manager in one sentence: Hey team, the deploy is postponed to Thursday because QA found a regression in the billing export; please do not merge anything into release until further notice.", "should_trigger": false},
  {"query": "make this message sound friendlier for my 10-year-old nephew: Hey team, the deploy is postponed to Thursday because QA found a regression in the billing export; please do not merge anything into release until further notice.", "should_trigger": false},
  {"query": "translate this into Spanish for my grandmother: Hey team, the deploy is postponed to Thursday because QA found a regression in the billing export; please do not merge anything into release until further notice.", "should_trigger": false},
  {"query": "my mom asked me what a VPN actually does. how do I explain it without the tech talk", "should_trigger": true},
  {"query": "explain what an index fund is to someone who has never invested", "should_trigger": true},
  {"query": "break down how a credit score works for a high school econ class", "should_trigger": true},
  {"query": "what's a docker container? explain it for a product manager who doesn't code", "should_trigger": true},
  {"query": "explain photosynthesis so my 8-year-old gets it", "should_trigger": true},
  {"query": "translate this legalese into plain English: The party of the first part shall indemnify and hold harmless the party of the second part from any and all claims arising out of or in connection with the performance of this agreement, except to the extent such claims result from the gross negligence of the party of the second part.", "should_trigger": true},
  {"query": "proofread my cover letter for grammar only, keep my wording: I am writing to apply for the data analyst position at your company. Over the last three years I have built dashboards for a logistics firm and lead a small team of two. I am excited about the chance to bring this experience to you're team and would welcome the opportunity to discuss it further.", "should_trigger": false},
  {"query": "translate this paragraph into French for my grandmother: Hey team, the deploy is postponed to Thursday because QA found a regression in the billing export; please do not merge anything into release until further notice.", "should_trigger": false}
]
```

- [ ] **Step 3: Give the two context-less queries something to write about.** In `evals/trigger-evals.json`, both misses were the model refusing to invent steps in an empty folder.

Line 6, replace the query text `write the restart steps for the nightly ETL so the on-call person can follow them half asleep` with `write the restart steps for the nightly ETL so the on-call person can follow them half asleep. it runs from cron at 02:00, takes a lock file, and loads into Postgres`.

Line 11, replace `write setup instructions for the fare-validation API that a transit agency IT person must follow` with `write setup instructions for the fare-validation API that a transit agency IT person must follow. they need an API key from our portal, the base URL, and a webhook URL for the validation results`.

- [ ] **Step 4: Check the files parse.**

Run: `python -c "import json; a=json.load(open('evals/trigger-evals.json',encoding='utf-8')); b=json.load(open('evals/trigger-heldout.json',encoding='utf-8')); print(len(a), sum(q['should_trigger'] for q in a), len(b), sum(q['should_trigger'] for q in b))" && python scripts/trigger_eval.py --help | head -3`
Expected: `20 10 16 11` and the usage line listing `--queries`, `--out`, `--ref`, `--model`.

- [ ] **Step 5: Smoke test with 4 headless sessions.** Write a 2-query file to your session scratchpad (never under a path containing "ste" or "trig"), then run it paired.

```bash
S="<your session scratchpad dir>"
printf '%s\n' '[{"query": "80% STE please: how does a heat pump work", "should_trigger": true}, {"query": "translate this doc to Spanish", "should_trigger": false}]' > "$S/smoke.json"
python scripts/trigger_eval.py --runs 1 --queries "$S/smoke.json" --out "$S/smoke.jsonl" --ref HEAD; echo "exit $?"
python -c "import json,sys; rows=[json.loads(l) for l in open(sys.argv[1],encoding='utf-8')]; print(len(rows), sorted({r['variant'] for r in rows}), all(r['valid'] for r in rows), sorted({r['model'] for r in rows}))" "$S/smoke.jsonl"
```
Expected: both descriptions printed (identical, since the working tree equals HEAD); `new run 1: should-trigger 1/1, should-not triggered 0/1` and the same for `old`; `invalid sessions (left out): 0/4`; `PASS`; `exit 0`; last line `4 ['new', 'old'] True [...]` with one model name. If the heat-pump query misses in one variant, rerun once; a second miss is a STOP (the script, not the skill, is then suspect).

- [ ] **Step 6: Commit.**

```bash
git add scripts/trigger_eval.py evals/trigger-heldout.json evals/trigger-evals.json
git commit -q -m "eval: paired trigger runs, held-out query file, context for two queries

trigger_eval.py now copies the plugin to a neutral temp dir, pairs old and
new descriptions in one batch with --ref, retries and excludes failed
sessions, and kills timed-out process trees on Windows.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 3: Pinned grading standards, helper scripts, criteria, docs

**Files:**
- Modify: `evals/evals.json` (add `grading_notes` to each of the 5 evals)
- Modify: `.claude/agents/grader.md` (steps 2 and 4)
- Create: `scripts/tabulate_eval.py`, `scripts/screen_blind.py`
- Modify: `.claude/commands/eval.md`, `.claude/commands/hillclimb.md`, `CLAUDE.md`
- Rewrite: `specs/success-criteria.md` (lines 1-21; the Hygiene section stays)

**Interfaces:**
- Produces: `python scripts/tabulate_eval.py workspace/iteration-N` (layout `workspace/iteration-N/<eval>/<arm>/run-K/{output.md,grading.json}`; arm is `with_skill` or `arm-*`).
- Produces: `python scripts/screen_blind.py make ITER EVAL KEY` and `python scripts/screen_blind.py tally ITER EVAL KEY [--field passed]`; graders write `ITER/blind/EVAL/grader-K.json` shaped `{"01": {"passed": true, ...}}`.

Note: agent and command files are read when a session starts. Edits here take effect in later sessions. That is why P2 carries the same instructions in every grader prompt.

- [ ] **Step 1: Add `grading_notes` to `evals/evals.json`.** In each eval object, add a `"grading_notes"` key after `"assertions"` (remember the comma after the assertions array).

oauth-simple:
```json
      "grading_notes": [
        "Assertion 2: use the delete-on-sight list in skills/ste-explain/references/rules.md. Frequency and limit words (often, about, usually) are not hedges.",
        "Assertion 4: a pronoun or a shortened form right after the full term (\"the old one\") is not rotation. A different noun for the same token is."
      ]
```
rewrite-dense:
```json
      "grading_notes": [
        "Assertion 2: apply the certainty rule in the fixture. Fact 7 passes when the need for board approval is stated plainly and the expectation covers the whole clause or the timing (\"The agency expects the purchase to need board approval in the second quarter\"). It fails when a hedge adverb sits on the need (\"will probably need\", \"will likely need\").",
        "Assertion 3: about, in most cases, and expects carry source meaning and are not hedges.",
        "Assertion 5: count real noun phrases. The linter's noun-cluster warnings include verbs and are only hints."
      ]
```
strict-bike-chain:
```json
      "grading_notes": [
        "Assertion 1: a step passes if it starts with an imperative verb, or with one condition or time clause (If, When, While, Before, After, Until) followed by a command in the same sentence. It fails if a place phrase or an adverb comes before the verb, or if the clause after the condition is a statement and the command comes in a later sentence.",
        "Assertion 2: count words per sentence. The 20-word limit applies to numbered steps and to the command sentence of a Warning or Caution. Notes and prose around the steps follow the 25-word limit. This matches scripts/ste_lint.py --procedure.",
        "Assertion 3: a state after a linking verb (is locked, is closed, is worn) is not passive.",
        "Assertion 4: test each warning against the first step that it applies to."
      ]
```
etl-runbook:
```json
      "grading_notes": [
        "Assertion 1: a step passes if it starts with an imperative verb, or with one condition or time clause (If, When, While, Before, After, Until) followed by a command in the same sentence. It fails if a place phrase or an adverb comes before the verb, or if the clause after the condition is a statement and the command comes in a later sentence.",
        "Assertion 2: count words per sentence. The 20-word limit applies to numbered steps and to the command sentence of a Warning or Caution. Notes and prose around the steps follow the 25-word limit. This matches scripts/ste_lint.py --procedure.",
        "Assertion 4: applies to every sentence, including notes and the intro. One imperative sentence that joins two commands with 'and' or 'then' fails. A command with a time clause (\"Kill the connection before you stop the job\") is one instruction."
      ]
```
jargon-translation:
```json
      "grading_notes": [
        "Assertion 3: usually, often, and may carry meaning and are not hedges.",
        "Assertion 5 has three parts and needs all three. Lag: a read can return old data. Condition: the text says that the copies match only when no new changes arrive; \"in the end\" or \"soon\" with no such condition does not count. No bound: no sentence states or implies a guaranteed time limit. \"soon\" and \"a short time\" are not bounds. A stated duration for how long agreement takes (\"within seconds\", \"after a few seconds all copies agree\") is a bound unless the text also says that the system promises no fixed time. Durations inside an analogy or example are not bounds when the condition is present. A one-line summary that drops the condition or adds a time limit fails."
      ]
```

Run: `python -c "import json; d=json.load(open('evals/evals.json',encoding='utf-8')); print([len(e['grading_notes']) for e in d['evals']], [len(e['assertions']) for e in d['evals']])"`
Expected: `[2, 3, 4, 3, 2] [5, 5, 5, 5, 5]`

- [ ] **Step 2: Pin the grader's output shape.** In `.claude/agents/grader.md` replace step 2 and step 4 (the JSON block included) with:

````
2. Check each remaining assertion by reading the output. Apply the eval's
   `grading_notes` from `evals/evals.json`: they are the standing reading of
   each assertion. Do not read gradings from other iterations to calibrate.
   For fact-preservation assertions, check every fact in the fixture's grader
   list, one by one; "mostly there" is a fail.
````
````
4. Write `grading.json` next to the output file, in exactly this shape (the
   viewer and scripts/tabulate_eval.py depend on it): one row per assertion,
   in the order given, and the quality judgment in its own key, never as an
   extra row.

```json
{
  "expectations": [
    {"text": "<assertion>", "passed": true, "evidence": "<quote or lint line>"}
  ],
  "quality": {"passed": true, "evidence": "<what is right or wrong beyond the rules>"}
}
```
````

- [ ] **Step 3: Create `scripts/tabulate_eval.py`.**

```python
#!/usr/bin/env python3
"""Tabulate one eval iteration: per-assertion pass/fail, points, lint errors.

Layout: workspace/iteration-N/<eval>/<arm>/run-K/{output.md,grading.json}.
<arm> is with_skill for a single-arm eval, or arm-a, arm-b, ... for a paired
batch. One letter per assertion row: P pass, F fail. A grading file that does
not have exactly 5 rows is flagged with "!" and only its first 5 rows count.
Points count every run present, so name supplementary runs when you report.

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
                marks.append("".join("P" if r["passed"] else "F" for r in rows) + flag)
                pts += sum(bool(r["passed"]) for r in rows)
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
```

Run: `python scripts/tabulate_eval.py workspace/iteration-13`
Expected:
```
rewrite-dense        with_skill   14  PFPPP PPPPP PPPPP  lint 0/0/0
strict-bike-chain    with_skill   14  PPPPP PPPPP PPPPF  lint 0/0/0
etl-runbook          with_skill   14  PPPPP FPPPP PPPPP  lint 0/0/0
TOTAL with_skill: 42
```

- [ ] **Step 4: Create `scripts/screen_blind.py`.**

```python
#!/usr/bin/env python3
"""Blind copies and a majority tally for a screen of several arms.

make   copies every ITER/EVAL/arm-*/run-*/output.md to ITER/blind/EVAL/NN.md
       in a seeded shuffled order and writes the key (NN -> arm, run) to KEY.
       Put KEY outside the repo so that graders cannot find it.
tally  reads ITER/blind/EVAL/grader-*.json, each {"NN": {"passed": bool, ...}},
       and prints per arm how many outputs a majority of graders passed. A
       1-1 split counts as a fail and is listed; add a third grader file that
       covers the split outputs and run tally again.

Usage:
  python3 scripts/screen_blind.py make  ITER EVAL KEY [--seed 14]
  python3 scripts/screen_blind.py tally ITER EVAL KEY [--field passed]
"""

import argparse
import json
import random
import shutil
from pathlib import Path


def make(it, ev, key_path, seed):
    outs = sorted((it / ev).glob("arm-*/run-*/output.md"))
    random.Random(seed).shuffle(outs)
    blind = it / "blind" / ev
    blind.mkdir(parents=True, exist_ok=True)
    key = {}
    for i, src in enumerate(outs, 1):
        nn = f"{i:02d}"
        shutil.copyfile(src, blind / f"{nn}.md")
        key[nn] = {"arm": src.parent.parent.name, "run": src.parent.name}
    key_path.write_text(json.dumps(key, indent=1), encoding="utf-8")
    print(f"{len(outs)} outputs copied to {blind}; key written to {key_path}")


def tally(it, ev, key_path, field):
    key = json.loads(key_path.read_text(encoding="utf-8"))
    files = sorted((it / "blind" / ev).glob("grader-*.json"))
    graders = [json.loads(p.read_text(encoding="utf-8")) for p in files]
    arms, split, ungraded = {}, [], []
    for nn, where in sorted(key.items()):
        votes = [bool(g[nn][field]) for g in graders if nn in g]
        if not votes:
            ungraded.append(nn)
            continue
        if len(set(votes)) > 1:
            split.append(nn)
        passed = sum(votes) * 2 > len(votes)
        arms.setdefault(where["arm"], []).append((where["run"], passed))
    for arm, runs in sorted(arms.items()):
        detail = " ".join(f"{r}:{'P' if p else 'F'}" for r, p in sorted(runs))
        print(f"{ev} {arm} {field}: {sum(p for _, p in runs)}/{len(runs)}  {detail}")
    print(f"grader files: {len(files)}")
    print(f"split votes: {', '.join(split) or 'none'}")
    print(f"ungraded: {', '.join(ungraded) or 'none'}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["make", "tally"])
    ap.add_argument("iteration")
    ap.add_argument("eval")
    ap.add_argument("key")
    ap.add_argument("--seed", type=int, default=14)
    ap.add_argument("--field", default="passed")
    args = ap.parse_args()
    it, key_path = Path(args.iteration), Path(args.key)
    if args.command == "make":
        make(it, args.eval, key_path, args.seed)
    else:
        tally(it, args.eval, key_path, args.field)


if __name__ == "__main__":
    main()
```

Run a dry check in your scratchpad (not in `workspace/`):
```bash
S="<your session scratchpad dir>"; mkdir -p "$S/it/demo/arm-a/run-1" "$S/it/demo/arm-b/run-1"
echo one > "$S/it/demo/arm-a/run-1/output.md"; echo two > "$S/it/demo/arm-b/run-1/output.md"
python scripts/screen_blind.py make "$S/it" demo "$S/key.json"
printf '%s' '{"01": {"passed": true}, "02": {"passed": false}}' > "$S/it/blind/demo/grader-1.json"
printf '%s' '{"01": {"passed": true}, "02": {"passed": true}}' > "$S/it/blind/demo/grader-2.json"
python scripts/screen_blind.py tally "$S/it" demo "$S/key.json"
```
Expected: `2 outputs copied ...`; then two arm lines, one `1/1` and one `0/1`; `grader files: 2`; `split votes: 02`; `ungraded: none`.

- [ ] **Step 5: Rewrite `.claude/commands/eval.md` body** (keep the frontmatter):

```
Run one eval iteration. Iteration name: $ARGUMENTS (if empty, use the next
number after the highest existing `workspace/iteration-*`).

Layout: `workspace/iteration-<N>/<eval-name>/<arm>/run-<K>/output.md`. The arm
is `with_skill` for a single-arm eval, or `arm-a`, `arm-b`, ... for a paired
batch. Run 3 runs per eval per arm.

1. Read `evals/evals.json`. For the rewrite eval, copy ONLY the paragraph of
   the fixture (the lines between the two `---` rules) to
   `workspace/iteration-<N>/rewrite-dense/input.md` and give testers that
   path. Never give a tester the fixture path: it holds the grader's facts.
2. In ONE turn, spawn a `skill-tester` subagent for every eval and run, all in
   parallel. Give each: the eval prompt, its input file, and the output path.
   Never run a tester in the main session — fresh context is the point.
   Baselines: reuse `workspace/iteration-6/<eval>/baseline/`. The baseline
   does not depend on the skill. Run `baseline-tester` only if they are gone.
3. As testers finish, spawn one `grader` subagent per output. Give it the eval
   name, the output path, the 5 assertions verbatim, and the eval's
   `grading_notes`. It writes `grading.json` next to the output: 5 rows plus
   a `quality` key.
4. Run `python3 scripts/tabulate_eval.py workspace/iteration-<N>` and write
   `workspace/iteration-<N>/summary.md`: the table (eval × assertions passed,
   per run, lint errors with-skill, lint errors baseline) plus each grader's
   most important failure, verbatim.
5. Show me the table and stop. Do NOT edit the skill in this command; that
   is /hillclimb's job.

Paired batch (what /hillclimb uses). One total is noise: the same text has
drawn 72/75 and 68/75. To judge an edit, run the committed text (arm-a) and
the edited text (arm-b) in the same session. Testers read a fixed path, so
run the arms as waves: apply the edit, run every tester of that arm, wait
until every output exists, undo the edit, then run the next arm.
```

- [ ] **Step 6: Update `.claude/commands/hillclimb.md`.** Replace steps 4 and 5 with:

```
4. **Re-measure.** Run /eval as a fresh iteration and as a paired batch:
   arm-a is the committed text, arm-b is the edit. Spawn a
   `red-team-reviewer` subagent on the new skill text in parallel.
5. **Decide.** Keep the edit only if its target assertion improves over arm-a
   in the same batch and arm-b's total is not more than 3 below arm-a's.
   Never compare with a total from an earlier iteration. A total that moves
   only through evals the edit cannot affect is noise.
6. **Log.** Append one row to `docs/hillclimb-log.md`: iteration, what
   changed (one line), assertions passed arm-a → arm-b, reviewer verdict.
```

- [ ] **Step 7: Update `CLAUDE.md`.** Replace lines 12-13 (the `trigger_eval.py` bullet) with:

```
- `python3 scripts/trigger_eval.py` — trigger evals via headless `claude -p`
  (3 runs × 20 queries). `--ref <git-ref>` pairs the old and new description
  in one batch; `--queries evals/trigger-heldout.json` runs the held-out set
- `python3 scripts/tabulate_eval.py workspace/iteration-N` — grades and lint
  errors per eval, arm and run
- `python3 scripts/screen_blind.py make|tally` — blind copies and majority
  tally when several arms are screened on one assertion
```

And add after workflow item 5:

```
6. Judge every edit against a control arm in the same batch, and every
   description edit with `trigger_eval.py --ref`. Totals and trigger rates
   from different days are not comparable.
```

- [ ] **Step 8: Rewrite lines 1-21 of `specs/success-criteria.md`** (keep the `## Hygiene` section below unchanged):

```
# Success criteria (definition of done for v1)

Measured by `/eval` (scripts/ste_lint.py + grader agent) and the trigger
evals. One batch is noise: the same skill text has drawn 72/75 and 68/75, and
the same description has triggered 26/30 one day and 22/30 the next. So each
output-quality threshold is a rate over 6 with-skill runs per eval (two
batches of 3) of the exact committed text. Exactly 4 of 6 means run one more
batch of 3 and pass at 7 of 9; 3 of 6 or fewer fails. Report the count for
each criterion; there is no single done flag.

## Output quality

- [ ] All 5 evals: zero lint errors (sentence length, paragraph length) in
      at least 5 of 6 with-skill runs per eval.
- [ ] Procedures (evals 3, 4): every step starts with a verb, or with a
      condition followed by a command, in at least 5 of 6 runs per eval;
      zero passive-voice sentences.
- [ ] Rewrite eval: all 8 fixture facts present with their certainty in at
      least 5 of 6 runs.
- [ ] Hedge/filler count: zero across all with-skill outputs.
- [ ] With-skill beats baseline on lint error count in every eval (sanity
      check that the skill is doing work).
- [ ] Grader's qualitative check passes in at least 5 of 6 runs per eval:
      correct, complete, natural.

## Triggering

Measured with `scripts/trigger_eval.py` (3 runs).

- [ ] At least 22 of 30 should-trigger hits on evals/trigger-evals.json. A
      lower count means that a stable query broke.
- [ ] At most 2 of 30 false triggers (the near-misses are the test).
- [ ] A description change is judged only against the old description in the
      same batch (`--ref`), on trigger-evals.json and trigger-heldout.json:
      at most 2 should-trigger hits below the old one per file, and at most
      1 more false trigger.
- Open defect: three should-trigger queries are unstable (OAuth "keep it
  simple", gradient descent "smart high schooler", fare-validation API).
```

- [ ] **Step 9: Verify and commit in two commits** (the spec change alone).

Run: `python scripts/ste_lint.py --self-test && python scripts/validate_skill.py && git status --short`
Expected: `self-test PASS`, `ok: ...`, and exactly these paths: `M .claude/agents/grader.md`, `M .claude/commands/eval.md`, `M .claude/commands/hillclimb.md`, `M CLAUDE.md`, `M evals/evals.json`, `M specs/success-criteria.md`, `?? scripts/screen_blind.py`, `?? scripts/tabulate_eval.py`.

```bash
git add specs/success-criteria.md
git commit -q -m "spec: success criteria as rates over six runs, trigger floor 22/30

One batch is noise (72/75 then 68/75 for one text; 26/30 then 22/30 for one
description), so \"100%, 3/3 runs\" could not be told from luck. Approved by
the user on 2026-10-04.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
git add evals/evals.json .claude/agents/grader.md .claude/commands/eval.md .claude/commands/hillclimb.md CLAUDE.md scripts/tabulate_eval.py scripts/screen_blind.py
git commit -q -m "eval: pin grading standards, add tabulate and blind-screen helpers

grading_notes in evals.json fix the reading of each assertion (verb-first,
note length, fact 7, the three parts of the timing assertion). Graders write
5 rows plus a quality key. /eval and /hillclimb document paired waves.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
git status --short
```
Expected: no output from the last command.

---

### Task 4: Screen three candidate edits (iteration-14)

**Files:** none committed. Working files under `workspace/iteration-14/`.

**Interfaces:**
- Consumes: P1, P3, `scripts/screen_blind.py`.
- Produces: the treatment `T` for Task 5 (one of `arm-cd`, `arm-c`, `arm-d`, or none), its patch file and its SKILL.md hash, and the screen counts J (jargon assertion 5 passes) and F (fact 7 passes) per arm.

Arms. `arm-a` is the committed text. The other three:

**arm-c** (self-check, SKILL.md lines 53-56). The one sentence from iteration-8 that fixed jargon, scoped to explanations so that it does not run in rewrite mode. Replace:
```
noun clusters, and hedges. Fix what you find, then answer. Do not show this
check to the user unless they ask for a rule report.
```
with:
```
noun clusters, and hedges. If you explained a topic, check each claim and any
one-line summary: do not make a claim stronger to make it simpler. Fix what
you find, then answer. Do not show this check to the user unless they ask for
a rule report.
```

**arm-d** (rule 4, SKILL.md lines 32-33). An example of the passing form, with no qualifier vocabulary. Replace:
```
4. Use the active voice. Name who or what does the action. Passive is
   acceptable only in descriptions when the actor is unknown.
```
with:
```
4. Use the active voice. Name who or what does the action: "The team expects
   delivery on Friday", not "Delivery is expected on Friday". Passive is
   acceptable only in descriptions when the actor is unknown.
```

**arm-cd** is both edits.

- [ ] **Step 1: Build the three patches.**

```bash
mkdir -p workspace/iteration-14/arms workspace/iteration-14/rewrite-dense
cp workspace/iteration-13/rewrite-dense/input.md workspace/iteration-14/rewrite-dense/input.md
```
Apply the arm-c replacement with the Edit tool, then:
```bash
python scripts/validate_skill.py && python scripts/ste_lint.py skills/ste-explain/SKILL.md | tail -1
git diff -- skills/ > workspace/iteration-14/arms/arm-c.patch && git apply -R workspace/iteration-14/arms/arm-c.patch && git status --short
```
Expected: `ok: ... body 66 lines`, a lint line that starts `0 error(s)` (the warning count may differ from 17), then no status output. Do the same for the arm-d replacement into `arm-d.patch` (body 65 lines). Then:
```bash
git apply workspace/iteration-14/arms/arm-c.patch && git apply workspace/iteration-14/arms/arm-d.patch
python scripts/validate_skill.py && python scripts/ste_lint.py skills/ste-explain/SKILL.md | tail -1
git diff -- skills/ > workspace/iteration-14/arms/arm-cd.patch && git apply -R workspace/iteration-14/arms/arm-cd.patch && git status --short
```
Expected: `body 67 lines`, `0 error(s)`, clean status. If lint reports an error for any arm, fix the wording so that every sentence is ≤25 words and the self-check paragraph is ≤6 sentences, rebuild the patch, and record the final wording in `workspace/iteration-14/waves.md`.

- [ ] **Step 2: Run 8 waves (P3), in this order.** Each wave launches its testers in one message.

| Wave | Arm | Patch | Runs | Testers |
| --- | --- | --- | --- | --- |
| 1 | arm-a | none | 1-3 | jargon-translation ×3, rewrite-dense ×3 |
| 2 | arm-c | arm-c.patch | 1-3 | jargon ×3, rewrite ×3 |
| 3 | arm-cd | arm-cd.patch | 1-3 | jargon ×3, rewrite ×3 |
| 4 | arm-d | arm-d.patch | 1-6 | rewrite ×6 |
| 5 | arm-a | none | 4-6 | jargon ×3, rewrite ×3 |
| 6 | arm-c | arm-c.patch | 4-6 | jargon ×3, rewrite ×3 |
| 7 | arm-cd | arm-cd.patch | 4-6 | jargon ×3, rewrite ×3 |
| 8 | arm-d | arm-d.patch | 7-12 | rewrite ×6 |

Output paths: `workspace/iteration-14/<eval>/<arm>/run-K/output.md`. After wave 8:

Run: `find workspace/iteration-14 -name output.md | wc -l && git status --short && cat workspace/iteration-14/waves.md`
Expected: `48`, clean status, 8 lines with 4 distinct hashes (arm-a twice the same, and so on).

- [ ] **Step 3: Lint all 48 outputs mechanically.**

Run: `for f in $(find workspace/iteration-14 -path '*/arm-*' -name output.md | sort); do echo "$(python scripts/ste_lint.py $f --json | python -c "import json,sys; print(len(json.load(sys.stdin)['errors']))") $f"; done | grep -v '^0 ' ; echo done`
Expected: only `done`. Record any file with errors for the summary.

- [ ] **Step 4: Make blind copies.**

```bash
S="<your session scratchpad dir>"
python scripts/screen_blind.py make workspace/iteration-14 jargon-translation "$S/key-jargon.json"
python scripts/screen_blind.py make workspace/iteration-14 rewrite-dense "$S/key-rewrite.json"
```
Expected: `18 outputs copied ...` and `30 outputs copied ...`.

- [ ] **Step 5: Grade blind, two graders per eval.** Launch 4 `general-purpose` subagents in one message (K = 1 and 2 for each eval). Do not use the `grader` agent here: it is pinned to 5 rows.

Jargon prompt:
```
You grade outputs for one assertion. You did not write them and you owe them nothing. Read only the files in the folder named below. Do not read any other file in workspace/.

Folder: workspace/iteration-14/blind/jargon-translation/ (files 01.md to 18.md). Each file answers this request: "my boss asked what 'eventual consistency' means. explain it so a non-engineer gets it".

Assertion: Technically correct: reads may lag writes; all replicas converge once writes stop, and no fixed delay is promised (an output that states or implies a set time limit fails).

Judge three parts for each file:
- lag: the text says that a read can return old data.
- condition: the text says that the copies match only when no new changes arrive (any wording: "if no new changes arrive", "once the changes stop"). "In the end" or "soon" with no such condition does not count.
- no_bound: no sentence states or implies a guaranteed time limit. "soon", "a short time" and "a moment" are not bounds. A stated duration for how long agreement takes ("within seconds", "from a fraction of a second to a few seconds", "after a few seconds all copies agree") is a bound unless the text also says that the system promises no fixed time. Durations inside an analogy or an everyday example are not bounds when condition is true.
A one-line summary counts: if it drops a condition that the body has, set condition to false; if it adds a time limit, set no_bound to false.
passed = lag and condition and no_bound.

Write one JSON file, workspace/iteration-14/blind/jargon-translation/grader-<K>.json, shaped:
{"01": {"passed": true, "lag": true, "condition": true, "no_bound": true, "evidence": "<the sentence or sentences that decide it, quoted>"}, "02": {...}}
Grade every file. Report back only: how many files passed, and the path of the JSON file.
```

Rewrite prompt:
```
You grade outputs for one assertion. You did not write them and you owe them nothing. Read only the files named below. Do not read any other file in workspace/.

Folder: workspace/iteration-14/blind/rewrite-dense/ (files 01.md to 30.md). Each file is a rewrite of the paragraph in workspace/iteration-14/rewrite-dense/input.md. Read that paragraph. Then read the section "Fact list (grader only)" in evals/fixtures/dense-paragraph.md, including its certainty rule.

Assertion: All 8 facts from the fixture's fact list are present, each with its original certainty.

For each file check all 8 facts one by one. A fact whose certainty changes counts as missing: a hedge added, removed, or moved to another claim.
fact7 is true when the need for board approval is stated plainly and the expectation covers the whole clause or the timing, as in "The agency expects the purchase to need board approval in the second quarter" or "The purchase needs board approval, expected in the second quarter". It is false when a hedge adverb sits on the need ("will probably need", "will likely need").
passed = all 8 facts present with their original certainty.

Write one JSON file, workspace/iteration-14/blind/rewrite-dense/grader-<K>.json, shaped:
{"01": {"passed": true, "fact7": true, "missing": [], "evidence": "<the sentence for fact 7, quoted, and the sentence for any missing fact>"}, "02": {...}}
Grade every file. Report back only: how many files passed, how many have fact7 true, and the path of the JSON file.
```

- [ ] **Step 6: Tally and break ties.**

```bash
python scripts/screen_blind.py tally workspace/iteration-14 jargon-translation "$S/key-jargon.json" --field passed
python scripts/screen_blind.py tally workspace/iteration-14 rewrite-dense "$S/key-rewrite.json" --field fact7
python scripts/screen_blind.py tally workspace/iteration-14 rewrite-dense "$S/key-rewrite.json" --field passed
```
If `split votes` lists any files, launch one more `general-purpose` grader per eval with the same prompt, K = 3, and the sentence "Grade only these files: <the split numbers>." added before "Write one JSON file". Run the three tally commands again; `split votes` may still list files, but each now has three votes and the majority decides.

- [ ] **Step 7: Apply the advance rules.** Let J(x) be jargon `passed` for arm x out of 6, and F(x) be rewrite `fact7` out of 6 (out of 12 for arm-d).

- STOP if J(arm-a) ≥ 3. The baseline moved; report and ask.
- arm-c passes if J(c) ≥ 4 and F(c) ≥ 4.
- arm-cd passes if J(cd) ≥ 4 and F(cd) ≥ 4.
- arm-d passes if F(d) = 12 of 12.
- Choose T: if arm-cd passes and arm-d passes, T = arm-cd. Else if arm-c passes, T = arm-c. Else if arm-cd passes, T = arm-cd. Else if arm-d passes, T = arm-d. Else T = none.

Why these numbers: the control has passed jargon assertion 5 in 0 of 12 runs, so 4 of 6 by chance is under 2%. A fact 7 rate of 0.33 clears "4 of 6" under 20% of the time and is then caught by the pooled rule in Task 5. arm-d at the base rate reaches 12 of 12 about 7% of the time.

- [ ] **Step 8: Write `workspace/iteration-14/summary.md` and one log row.** The summary holds: the four arm texts, the waves and hashes, a table (arm × J, F, rewrite all-8-facts, lint errors), split votes and how they resolved, verbatim failing sentences (two per arm at most), the choice of T with the rule that produced it, and usage (48 testers, grader count, tokens from the task notifications). Add a row at the top of the table in `docs/hillclimb-log.md`:

`| iteration-14 | <date> | Screen, no skill change: arm-c (self-check "do not make a claim stronger to make it simpler", explanations only), arm-d (rule 4 example), arm-cd, 6 runs each on jargon and rewrite, blind dual grading — J a/c/cd = <n>/<n>/<n> of 6; fact 7 a/c/cd = <n>/<n>/<n> of 6, d = <n> of 12; advancing: <T> | — | — |`

```bash
git add docs/hillclimb-log.md && git commit -q -m "eval: log iteration-14 screen

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 5: Paired confirm, hygiene decision (iteration-15)

**Files:**
- Modify only if kept: `skills/ste-explain/SKILL.md`, `skills/ste-explain/references/rules.md`, `.claude-plugin/plugin.json`, `docs/hillclimb-log.md`

**Interfaces:**
- Consumes: T, its patch and hash from Task 4; `workspace/iteration-12/hygiene-bundle.patch`; P1 to P4; `scripts/tabulate_eval.py`; `scripts/trigger_eval.py --ref`.

Arms: `arm-a` committed text (5 evals × 3 runs). `arm-t` committed text + T (5 evals × 3 runs; skip this arm if T = none). `arm-h` committed text + hygiene bundle (rewrite-dense, strict-bike-chain, etl-runbook × 3 runs).

If `workspace/iteration-12/hygiene-bundle.patch` is missing, rebuild it with these edits and `git diff -- skills/ > workspace/iteration-15/hygiene-bundle.patch`, then reverse it:
- SKILL.md description tail: `tone changes ("more professional"), or translation.` → `tone changes ("more professional"), translation into another language, or grammar-only proofreading.`
- rules.md: `rotation is a style habit; here it is a defect.` → `rotation is a style habit. Here it is a defect.`
- rules.md: `(in aviation: part names; in software: API, token, commit). Use as few as` + next line `the topic needs, and use each one consistently.` → `(part names in aviation, or API, token, and commit in software). Use as few` + `as the topic needs, and use each one consistently.`
- rules.md: `only when the actor is unknown or irrelevant.` → `only when the actor is unknown.`
- rules.md: `better; do not pad to the limit.` → `better. Do not pad to the limit.`
- rules.md: `Avoid semicolons; write two` + `sentences instead.` → `Do not use semicolons. Write` + `two sentences instead.`
- rules.md checklist: `3. No passive voice in instructions; passive in descriptions only with an` → `3. No passive voice in instructions. In descriptions, passive only with an`

- [ ] **Step 1: Prepare.**

```bash
mkdir -p workspace/iteration-15/rewrite-dense
cp workspace/iteration-13/rewrite-dense/input.md workspace/iteration-15/rewrite-dense/input.md
git apply --check workspace/iteration-12/hygiene-bundle.patch && echo hygiene-ok
```
Expected: `hygiene-ok`.

- [ ] **Step 2: Wave 1, arm-a (P3).** 15 testers in one message: 5 evals × runs 1-3, paths `workspace/iteration-15/<eval>/arm-a/run-K/output.md`. As outputs land, launch one standard grader per output (P2). Bike testers take 15 to 30 minutes; do not start wave 2 until all 15 outputs exist.

- [ ] **Step 3: Wave 2, arm-t (P3), skipped if T = none.** Apply T's patch; `git hash-object skills/ste-explain/SKILL.md` must equal the hash recorded for that arm in `workspace/iteration-14/waves.md` (if not, STOP). Launch 15 testers to `.../arm-t/run-K/`, and in the same message the red-team reviewer (P4). Grade as outputs land. Reverse the patch only after all 15 outputs exist.

- [ ] **Step 4: Wave 3, arm-h (P3).** Apply the hygiene patch. Launch 9 testers: rewrite-dense, strict-bike-chain, etl-runbook × runs 1-3 to `.../arm-h/run-K/`. Grade as outputs land. Reverse the patch after all 9 outputs exist.

- [ ] **Step 5: Tabulate.**

Run: `python scripts/tabulate_eval.py workspace/iteration-15 && git status --short`
Expected: one line per eval and arm with 3 five-letter marks and no `!`, `ungraded` or `no-output`; `TOTAL arm-a`, `TOTAL arm-h`, `TOTAL arm-t`; clean status. Regrade any output whose grading file is flagged `!` with a fresh grader.

- [ ] **Step 6: Decide T.** From the grading files read jargon assertion 5 (row 5 of jargon-translation) and fact 7 (row 2 of rewrite-dense; the grader's evidence names fact 7 when it fails). Keep T only if all of these hold:

1. `TOTAL arm-t` ≥ `TOTAL arm-a` − 3.
2. In no eval is arm-t more than 2 points below arm-a.
3. If T contains arm-c: jargon assertion 5 pooled over screen and confirm ≥ 6 of 9, that is J(T) + (confirm passes of 3) ≥ 6.
4. Fact 7 pooled for T's text: for arm-c or arm-cd, F(T) + (confirm rewrite row-2 passes of 3) ≥ 7 of 9; for arm-d, ≥ 14 of 15.
5. The red-team verdict is not MAJOR ISSUES.

If T is kept: apply its edit with the Edit tool (same replacement text as the patch), set `"version"` in `.claude-plugin/plugin.json` to the next patch number, add the log row, and commit. For arm-cd make two commits, rule 4 first, each with its own version bump:

```bash
git add skills/ste-explain/SKILL.md .claude-plugin/plugin.json docs/hillclimb-log.md
git commit -q -m "feat: <rule 4 names the actor of an expectation | self-check stops explanations from overstating a claim>

<two lines: screen and confirm counts for the target, arm-a and arm-t totals>

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```
If T is not kept, change nothing under `skills/` and log the row as **not kept** with the rule that failed.

- [ ] **Step 7: Decide the hygiene bundle.** Let `a45` and `h45` be the arm-a and arm-h points on rewrite-dense + strict-bike-chain + etl-runbook (45 each, from the tabulate lines). Apply the bundle unless `h45 ≤ a45 − 3`.

If it applies: `git apply workspace/iteration-12/hygiene-bundle.patch` (on top of any kept T), then run the paired trigger guard before committing:

Run: `python scripts/trigger_eval.py --ref HEAD --workers 6 --out workspace/trigger-results-it15.jsonl; echo "exit $?"`
Expected: two different descriptions printed (the new one ends "translation into another language, or grammar-only proofreading."), per-query table, `PASS`, `exit 0`. About 120 sessions, 40 to 60 minutes. Exit 2 is a STOP. Exit 1 means the description costs triggers: run `git checkout -- skills/ste-explain/SKILL.md` to drop only the description hunk, keep the rules.md hunks, and say so in the log row.

Then validate, lint both files (`python scripts/ste_lint.py skills/ste-explain/references/rules.md | tail -1` must show `0 error(s)`), bump the version, add the log row, and commit:

```bash
git add skills/ .claude-plugin/plugin.json docs/hillclimb-log.md
git commit -q -m "fix: hygiene bundle (description exclusions, rules.md passive rule and semicolons)

Paired in iteration-15: arm-h <h45>/45 against arm-a <a45>/45. Trigger guard
paired with --ref: new <n>/30, old <n>/30, false triggers <n> and <n>.

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```
If it does not apply, log the row as **left out** with both subtotals.

- [ ] **Step 8: Write `workspace/iteration-15/summary.md`.** The tabulate table, the three decisions with the numbers each rule used, each grader's most important failure verbatim, the red-team findings, and usage.

---

### Task 6: Status of the final text (iteration-16)

**Files:** none modified except `docs/hillclimb-log.md`.

- [ ] **Step 1: Decide whether a batch is needed.** If Task 5 changed nothing under `skills/` (T not kept and the hygiene bundle left out), the final text is the committed text of iteration-15 arm-a: skip to Step 3 and use arm-a (3 runs) plus `workspace/iteration-11` (3 runs of the same text, older graders) as the 6 runs. Otherwise run one batch.

- [ ] **Step 2: Run one batch of the final text.** `git status --short` must be clean. `mkdir -p workspace/iteration-16/rewrite-dense && cp workspace/iteration-13/rewrite-dense/input.md workspace/iteration-16/rewrite-dense/input.md`. Launch 15 testers (P1) to `workspace/iteration-16/<eval>/with_skill/run-K/output.md`, grade each (P2), then `python scripts/tabulate_eval.py workspace/iteration-16`.

- [ ] **Step 3: Record the trigger baseline** if Task 5 Step 7 did not already run a paired trigger batch on the final description.

Run: `python scripts/trigger_eval.py --workers 6 --out workspace/trigger-results-it16.jsonl; echo "exit $?"`
Expected: per-run lines, per-query table, `PASS` or `FAIL` against 22/30 and 2/30. Report the three unstable queries' counts.

- [ ] **Step 4: Report each success criterion as a count.** For the exact final text, list per criterion in `specs/success-criteria.md` the runs that pass over the runs that exist (6 where two batches of the same text exist, 3 otherwise, and say which). Do not print a single done flag. Write `workspace/iteration-16/summary.md` with that list and add a log row.

```bash
git add docs/hillclimb-log.md && git commit -q -m "eval: log iteration-16 status of the final text

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 7: Package, record, push, report

- [ ] **Step 1: Package.** `python scripts/ste_lint.py skills/ste-explain/SKILL.md | tail -1 && python scripts/package_skill.py && python -c "import zipfile; print(zipfile.ZipFile('dist/ste-explain.zip').namelist())"`
Expected: `0 error(s)`, `wrote ...dist\ste-explain.zip`, a list with `ste-explain/SKILL.md` and `ste-explain/references/rules.md`.

- [ ] **Step 2: Update project memory.** In `eval-run-conventions.md` (project memory dir) add: the new commands (`trigger_eval.py --ref`, `tabulate_eval.py`, `screen_blind.py`), the screen-then-confirm design, and the outcome for each of arm-c, arm-d, arm-cd and the hygiene bundle. Remove the line that says the hygiene bundle is pending.

- [ ] **Step 3: Push.** `git push origin main && git rev-list --left-right --count origin/main...main` → `0	0`.

- [ ] **Step 4: Final report to the user.** Lead with what was kept and the plugin version. Then: the screen table, the confirm table, the criteria counts, trigger numbers, what is still failing, usage (subagent runs, headless sessions, token totals), and one line saying that `dist/ste-explain.zip` is ready to upload at claude.ai under Settings, Capabilities (the uploaded copy still has the pre-iteration-9 description).

---

## Verification (end to end)

- `python scripts/ste_lint.py --self-test` prints `self-test PASS`; `python scripts/validate_skill.py` prints `ok:`; `python scripts/ste_lint.py skills/ste-explain/SKILL.md` and `.../references/rules.md` report `0 error(s)`.
- `python scripts/tabulate_eval.py workspace/iteration-15` shows every run graded with 5 rows and no `!`.
- `workspace/iteration-14/waves.md` has 8 wave lines; every decision in Tasks 4 and 5 quotes the rule and the numbers it used.
- `git status --short` is empty; `git log --oneline` shows the Task 1 to 3 commits, the iteration-14 log commit, zero to three kept-change commits each with a version bump, and the iteration-16 log commit; `origin/main` equals `main`.
- `docs/hillclimb-log.md` has rows for iterations 14, 15 and 16, newest first.

## Budget (estimates from the last session's task notifications)

| Stage | Subagent runs | Headless sessions | Est. subagent tokens |
| --- | --- | --- | --- |
| Tasks 1-3 tooling | 0 | 4 (smoke) | — |
| Task 4 screen | 48 testers + 4 to 6 graders | 0 | about 1.5M |
| Task 5 confirm | 39 testers + 39 graders + 1 reviewer (24 + 24 if T = none) | 120 if the bundle applies | about 2.7M (1.5M if T = none) |
| Task 6 status | 15 + 15 (0 if nothing kept) | 60 unless Task 5 ran the guard | about 1.0M |

Total about 5M subagent tokens when an edit advances, about 3M when none does. The last session used about 4M.

## Backlog (not in this plan)

- Rule 10 says a vertical list for "more than three items"; the bike assertion wants the tools list vertical at any length (one failure, iteration-13 run 3).
- "Wait, then repeat ..." sentences now appear inside notes (etl, iteration-12 run 2).
- Red-team wording for rule 11: "In a step, only a condition may come before the verb"; a warning on its own line in 80% mode.
- OAuth answers run 330 to 400 words for "keep it simple".
- `rules.md` delete-on-sight list holds degree words (somewhat, fairly); `ste_lint.py` noun-cluster warnings count verbs.
- If neither arm fixes jargon assertion 5: propose to the user that timing correctness moves from an assertion to the quality check. That is a spec decision.
