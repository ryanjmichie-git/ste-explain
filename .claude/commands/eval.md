---
description: Run all evals (with-skill + baseline), grade them, and summarize
---

Run one full eval iteration. Iteration name: $ARGUMENTS (if empty, use the
next number after the highest existing `workspace/iteration-*`).

1. Read `evals/evals.json`. Create `workspace/iteration-<N>/<eval-name>/`
   for each eval as you go — nothing upfront.
2. In ONE turn, spawn for every eval BOTH a `skill-tester` and a
   `baseline-tester` subagent, all in parallel. Give each: the eval prompt,
   its input files, and an output path
   (`.../with_skill/output.md` or `.../baseline/output.md`). Never run a
   tester in the main session — fresh context is the point.
3. As testers finish, spawn a `grader` subagent per eval for the with-skill
   output. For baselines, just run
   `python3 scripts/ste_lint.py <output>` yourself and record the error and
   warning counts (they exist to show the delta, not to pass).
4. Write `workspace/iteration-<N>/summary.md`: one table —
   eval × (assertions passed, lint errors with-skill, lint errors baseline)
   — plus each grader's most important failure, verbatim.
5. Show me the table and stop. Do NOT edit the skill in this command; that
   is /hillclimb's job.
