# ste-explain

**Make AI output readable.** A tiny Claude Skill that applies ASD-STE100
(Simplified Technical English) — the controlled language behind aircraft
maintenance manuals — to any explanation or rewrite, softened to the
pragmatic "80%" mode [Andrej Karpathy recommends](https://x.com/karpathy/status/2105819303471976479).

No scripts. No dependencies. One SKILL.md that works on claude.ai, Claude
Code, and the Claude API.

## Before / after

> **Before:** "Essentially, the token refresh mechanism is leveraged by the
> client in order to facilitate the re-establishment of authenticated
> sessions without user re-engagement being required."
>
> **After:** "The client uses the refresh token to get a new session. The
> user does not log in again."

## Install

**claude.ai** — download `ste-explain.zip` from the latest release, then
Settings → Capabilities → upload the zip as a skill.

**Claude Code** (plugin):

```
claude plugin marketplace add ryanjmichie-git/ste-explain
/plugin install ste-explain@ste-explain
```

**Claude Code** (manual): copy `skills/ste-explain/` into `~/.claude/skills/`
(all projects) or `.claude/skills/` (one project).

**Claude API**: upload the skill folder via the `/v1/skills` endpoint and
reference it from the code execution container.

## Use

Just ask normally — the skill triggers on intent:

- "explain how OAuth refresh tokens work, keep it simple"
- "rewrite this paragraph so it's easier to read"
- "write the restart steps so the on-call person can follow them"
- "full strict STE" → applies the vocabulary discipline too

## What it enforces

Sentences of at most 20 words (instructions) or 25 (descriptions). One
instruction per sentence, verb first. Active voice. One meaning per word, no
synonym rotation. Conditions and warnings before the step. No hedges or
filler. See `skills/ste-explain/SKILL.md` — it is short on purpose.

## Developing

This repo is also the dev harness: `specs/` holds the contract, `evals/` the
graded test cases, `scripts/` the deterministic linter, and `.claude/` the
subagents, slash commands, and hooks for the improvement loop. Open the repo
in Claude Code and run `/eval`, then `/hillclimb`. `CLAUDE.md` has the rules.

## License and credits

MIT for everything in this repo. ASD-STE100 is a specification of ASD
(AeroSpace, Security and Defence Industries Association of Europe); get the
official spec free at [asd-ste100.org](https://www.asd-ste100.org). This
project distills the ideas in original wording and is not affiliated with or
endorsed by ASD. Idea sparked by Karpathy's post; this is an independent
implementation.
