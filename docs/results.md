# Results for v0.1.5

This file holds the measured state of the v0.1.5 skill text. That text is
SKILL.md blob `82b0c9a` and rules.md blob `8fc1996`, first committed in
`019bb11`. The raw
outputs stay local in `workspace/`, which git ignores. The numbers below come
from those outputs and from `docs/hillclimb-log.md`.

## Method

- **Evals.** `evals/evals.json` has five evals with five assertions each. A
  `skill-tester` subagent writes each output with the skill. A separate
  `grader` subagent grades it, and `scripts/ste_lint.py` does the mechanical
  checks. The grading rules are in `.claude/agents/grader.md` and in the
  `grading_notes` of each eval. The tester always has the skill, so these
  scores measure the output when the skill fires. The trigger tests measure
  whether it fires.
- **Runs.** Iteration 16 ran all five evals three times on 2026-10-04.
  Iteration 15 (arm-h) ran the rewrite, bike, and ETL evals three more times
  on the same text, on the same day.
- **Baseline.** Iteration 6 (2026-10-02) ran each eval three times with no
  skill. The current linter re-counted those outputs. This is an earlier
  batch, so compare it loosely.
- **Triggering.** `scripts/trigger_eval.py` ran headless `claude -p` sessions
  from an empty temp dir, with a plugin copy at a neutral path. Each query ran
  three times on claude-opus-5[1m], the CLI default, on 2026-10-04.

## Eval assertions (iteration 16)

| Eval | Prompt | Passed | Lint errors per run |
| --- | --- | --- | --- |
| oauth-simple | explain how OAuth refresh tokens work, keep it simple | 15 of 15 | 0, 0, 0 |
| rewrite-dense | rewrite this paragraph so it's easier to read (`evals/fixtures/dense-paragraph.md`) | 14 of 15 | 0, 0, 0 |
| strict-bike-chain | write the steps to replace a bicycle chain, full strict STE | 14 of 15 | 0, 0, 0 |
| etl-runbook | write a short runbook for restarting our nightly ETL job when it hangs ... | 15 of 15 | 0, 0, 0 |
| jargon-translation | my boss asked what 'eventual consistency' means. explain it so a non-engineer gets it | 12 of 15 | 0, 0, 0 |
| **Total** | | **70 of 75** | **0** |

The before and after in the README is iteration 16, rewrite-dense run 1,
unedited. It passed 5 of 5 assertions, so it kept all 8 facts with their
certainty. The input is one sentence of 128 words. The output has 10
sentences, and the longest has 21 words.

## Lint errors with and without the skill

A lint error is a sentence over the limit or a paragraph over six sentences.
The limit is 25 words, or 20 words for steps and warnings in the two
procedure evals.

| Eval | With the skill (iterations 15 and 16) | Without the skill (iteration 6) |
| --- | --- | --- |
| oauth-simple | 0 in 3 runs | 2, 1, 1 |
| rewrite-dense | 0 in 6 runs | 1, 2, 1 |
| strict-bike-chain | 0 in 6 runs | 0, 1, 0 |
| etl-runbook | 0 in 6 runs | 3, 3, 3 |
| jargon-translation | 0 in 3 runs | 1, 1, 0 |
| **Total** | **0 errors in 24 runs** | **20 errors in 15 runs; 3 of 15 runs clean** |

## Success criteria

These rows count the runs against `specs/success-criteria.md`. Rewrite, bike,
and ETL have 6 runs. OAuth and jargon have 3 runs.

| Criterion | Count | Status |
| --- | --- | --- |
| Zero lint errors in at least 5 of 6 runs per eval | every eval clean in every run | met |
| Procedure steps start with a verb, or a condition and a command | bike 6 of 6, ETL 6 of 6 | met |
| Rewrite keeps all 8 facts with their certainty | 3 of 6 | **not met** |
| No hedges or filler | 0 linter hedge warnings in 24 outputs | met |
| With the skill beats without on lint errors | 5 of 5 evals | met |
| Grader quality check in at least 5 of 6 runs | rewrite 5 of 6, jargon 2 of 3, others all | **jargon not met** |
| At least 22 of 30 should-trigger hits | 26 of 30 | met |
| At most 2 of 30 false triggers | 0 of 30 | met |

## Triggering per query

Standard set (`evals/trigger-evals.json`):

| Should trigger | Loaded the skill |
| --- | --- |
| 80% STE please: how does a heat pump work | 3 of 3 |
| can you rewrite this README section so new users can actually follow it? ... | 3 of 3 |
| explain gradient descent like i'm a smart high schooler | 3 of 3 |
| my boss asked what eventual consistency means, explain it so a non-engineer gets it | 3 of 3 |
| this paragraph from our SOP is unreadable, simplify it but keep everything: ... | 3 of 3 |
| use ASD-STE100 for this: ... | 3 of 3 |
| write setup instructions for the fare-validation API ... | 3 of 3 |
| write the restart steps for the nightly ETL so the on-call person can follow them half asleep ... | 3 of 3 |
| what does this error mean? explain simply: ECONNREFUSED 127.0.0.1:5432 | 2 of 3 |
| explain how OAuth refresh tokens work, keep it simple | 0 of 3 |

None of the ten near-miss queries loaded the skill (0 of 30). They ask for a
summary, a `TL;DR`, a more professional tone, or a more persuasive essay.
Others ask for a translation, proofreading, a shorter tweet, poem symbolism,
action items, or Shakespearean English.

Held-out set (`evals/trigger-heldout.json`):

| Should trigger | Loaded the skill |
| --- | --- |
| explain how vaccines train the immune system, I need to tell my grandma | 3 of 3 |
| explain photosynthesis so my 8-year-old gets it | 3 of 3 |
| explain what an index fund is to someone who has never invested | 3 of 3 |
| my mom asked me what a VPN actually does. how do I explain it without the tech talk | 3 of 3 |
| our sales team keeps asking what Kubernetes is. give me an explanation they'd get | 3 of 3 |
| what's a docker container? explain it for a product manager who doesn't code | 3 of 3 |
| explain what a mortgage escrow account is in layman's terms | 2 of 3 |
| no jargon please: what does a CDN do? | 2 of 3 |
| translate this legalese into plain English: ... | 1 of 3 |
| I'm new to Rust, explain lifetimes | 0 of 3 |
| break down how a credit score works for a high school econ class | 0 of 3 |
| **Total** | **23 of 33** |

One held-out near-miss loaded the skill in 1 of 3 sessions: "make this
message sound friendlier for my 10-year-old nephew". The other four loaded it
in 0 of 12 sessions.

## Failures, quoted from the graders

- **Jargon assertion 5, 0 of 3.** No run says that the copies match only when
  no new changes arrive. Run 1 defines the term as "Eventual consistency means
  that all copies of the data match after a short delay, not immediately."
  Run 3 adds a time bound: "In most systems, this delay is a few seconds or
  less."
- **Rewrite fact 7, 3 of 6.** The input says that the purchase "is
  anticipated to require board approval in the second quarter". Iteration 16
  run 3 wrote: "The purchase of this capability will probably need board
  approval in the second quarter." The two runs of iteration 15 that failed
  wrote "will probably need" too.
- **Bike assertion 5, 5 of 6.** One run named the two tools in a sentence,
  not in a vertical list. It wrote: "You need a chain tool and a new chain
  with a master link."

## Install checks (2026-10-05)

| Route | Check | Result |
| --- | --- | --- |
| Claude Code plugin | `claude plugin marketplace add` from a clean clone and `claude plugin install`, in an empty config dir | installed 0.1.5, enabled |
| Claude Code plugin | `claude plugin details` | 1 skill, no agents, hooks, or MCP servers; about 183 tokens in every session, about 790 more when it fires (estimate) |
| Claude Code plugin | one headless session with the installed copy: "80% STE please: how does a heat pump work" | skill loaded and called; 0 lint errors in the reply |
| Claude Code manual | the release zip unzipped into a project's `.claude/skills/`, then the same prompt | skill loaded and called; 0 lint errors in the reply |
| claude.ai | upload of the zip | not checked here |
| Claude API | Skills API upload | not checked here |

## Copyright spot check (2026-10-05)

Every tracked file was compared with distinctive rule wording from
ASD-STE100. The only shared runs of four or more words are common phrases,
such as "one instruction per sentence" and "use a vertical list for". This
check did not use the full text of the specification.

## Cost of one eval batch

Iteration 16 used 15 tester runs and 15 grader runs. Testers used 882,286
subagent tokens, graders used 683,564, and the total was 1,565,850.
