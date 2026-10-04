---
description: Run all evals (with-skill + baseline), grade them, and summarize
---

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
