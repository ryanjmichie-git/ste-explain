---
description: Eval → diagnose → minimal edit → re-eval loop on the skill, logged
---

Run $ARGUMENTS climb(s) (default 1). One climb is:

1. **Measure.** If the latest `workspace/iteration-*/summary.md` reflects
   the current skill, reuse it; otherwise run /eval first.
2. **Diagnose.** Read the failing graders' evidence and the tester outputs
   themselves, not just scores. Ask: is this one bad output, or a rule the
   skill states badly? Fixes must generalize — these five evals stand in
   for a million future prompts. If a change only helps one eval, it is
   overfitting; find the principle behind the failure instead, and prefer
   explaining why over adding an ALL-CAPS MUST.
3. **Edit minimally.** Propose the smallest change to
   `skills/ste-explain/SKILL.md` (or `references/rules.md`), show me the
   diff with one sentence of reasoning, then apply it. Prefer deleting a
   confusing line over adding a clarifying one.
4. **Re-measure.** Run /eval as a fresh iteration. Spawn a
   `red-team-reviewer` subagent on the new skill text in parallel.
5. **Log.** Append one row to `docs/hillclimb-log.md`: iteration, what
   changed (one line), assertions passed before → after, reviewer verdict.

Stop early and tell me when: everything in `specs/success-criteria.md`
passes, OR two consecutive climbs make no progress (then propose a
different angle instead of a third tweak), OR a change would violate
specs/skill-spec.md.
