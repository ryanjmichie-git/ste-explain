# Hillclimb log

One row per climb, appended by /hillclimb. Newest first. "Passed" counts
assertions across all five evals (see evals/evals.json for the denominator).

| Iteration | Date | Change (one line) | Passed before → after | Red-team verdict |
| --- | --- | --- | --- | --- |
| iteration-3 | 2026-10-02 | Rule 12: add "Filler adds no fact. A real limit (…) is a fact: keep it on the claim it limits." — **reverted** (flat; new line has defects) | 23/25 → 23/25 (before = it2 re-graded under tightened assertions) | MINOR ISSUES (5); not overfit, but self-contradicts on "arguably" |
| iteration-2 | 2026-10-02 | Rewrite note: "Offer a one-line note on which rules did the most work" → "End with one short sentence that names the rules that did the most work" | 24/25 → 25/25 | MINOR ISSUES (10); change judged not overfit |
