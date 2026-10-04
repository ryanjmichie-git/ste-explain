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

## Hygiene

- [ ] `python3 scripts/validate_skill.py` exits 0.
- [ ] `python3 scripts/ste_lint.py skills/ste-explain/SKILL.md` exits 0
      (the skill obeys its own rules).
- [ ] No text copied from the ASD-STE100 spec (spot-check by searching
      distinctive spec phrasings).
- [ ] Fresh-machine install verified for all three routes: claude.ai zip,
      Claude Code plugin, manual folder copy.
