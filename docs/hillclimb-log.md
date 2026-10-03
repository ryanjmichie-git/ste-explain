# Hillclimb log

One row per climb, appended by /hillclimb. Newest first. "Passed" counts
assertions across all five evals (see evals/evals.json for the denominator).

| Iteration | Date | Change (one line) | Passed before → after | Red-team verdict |
| --- | --- | --- | --- | --- |
| iteration-8 | 2026-10-02 | Climb 3 v2, 3 runs: rule 12 keeps real limits + "Do not make a claim stronger"; drop "arguably"; self-check "filler" — **reverted** (target jargon 13→15, but rewrite fact 7 13←14 via one-directional wording) | 69/75 → 69/75 | MINOR ISSUES (4); earlier flags fixed; #1 explains rewrite loss |
| iteration-7 | 2026-10-02 | Climb 5 re-test, 3 runs: "names the rules that did the most work" → "says what you changed" — **reverted** (target eval flat 14→14; total -1 from etl variance) | 69/75 → 68/75 | SOUND (reused from iteration-5) |
| iteration-6 | 2026-10-02 | M0: no skill change; switch to 3 runs per eval per condition (denominator 75) | — → 69/75 | — |
| iteration-5 | 2026-10-02 | Rewrite note: "names the rules that did the most work" → "says what you changed" — **reverted** (score drop; drop was in etl-runbook, which this change cannot affect) | 24/25 → 23/25 | MINOR ISSUES (4); change itself SOUND |
| iteration-4 | 2026-10-02 | Delete the rewrite example (it repeated the eval-2 prompt word for word) — kept | 23/25 → 24/25 (+1 is rewrite fact 7; likely variance) | MINOR ISSUES (3); deletion loses nothing |
| iteration-3 | 2026-10-02 | Rule 12: add "Filler adds no fact. A real limit (…) is a fact: keep it on the claim it limits." — **reverted** (flat; new line has defects) | 23/25 → 23/25 (before = it2 re-graded under tightened assertions) | MINOR ISSUES (5); not overfit, but self-contradicts on "arguably" |
| iteration-2 | 2026-10-02 | Rewrite note: "Offer a one-line note on which rules did the most work" → "End with one short sentence that names the rules that did the most work" | 24/25 → 25/25 | MINOR ISSUES (10); change judged not overfit |
