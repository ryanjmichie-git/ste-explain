# Success criteria (definition of done for v1)

Measured by `/eval` (scripts/ste_lint.py + grader agent) and the trigger
evals. All thresholds on 3 consecutive runs to control variance.

## Output quality

- [ ] All 5 evals: every lint error class at zero (sentence length,
      paragraph length) in with-skill outputs.
- [ ] Procedures (evals 3, 4): 100% of steps start with a verb; zero
      passive-voice sentences.
- [ ] Rewrite eval: all 8 fixture facts present in the output, 3/3 runs.
- [ ] Hedge/filler count: zero across all with-skill outputs.
- [ ] With-skill beats baseline on lint error count in every eval (sanity
      check that the skill is doing work).
- [ ] Grader's qualitative check passes: correct, complete, natural.

## Triggering

- [ ] ≥9/10 should-trigger queries trigger.
- [ ] ≤1/10 should-not-trigger queries trigger (the near-misses are the test).

## Hygiene

- [ ] `python3 scripts/validate_skill.py` exits 0.
- [ ] `python3 scripts/ste_lint.py skills/ste-explain/SKILL.md` exits 0
      (the skill obeys its own rules).
- [ ] No text copied from the ASD-STE100 spec (spot-check by searching
      distinctive spec phrasings).
- [ ] Fresh-machine install verified for all three routes: claude.ai zip,
      Claude Code plugin, manual folder copy.
