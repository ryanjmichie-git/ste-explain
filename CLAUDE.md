# ste-explain — dev guide

The product is one skill: `skills/ste-explain/` (SKILL.md + references/rules.md).
Everything else in this repo exists to measure and improve it. Read
`specs/skill-spec.md` before changing the skill; it is the contract.

## Commands

- `python3 scripts/ste_lint.py <file>` — deterministic STE structure check
  (`--procedure` for 20-word limit, `--json`, `--self-test`)
- `python3 scripts/validate_skill.py` — frontmatter + size constraints
- `python3 scripts/trigger_eval.py` — trigger evals via headless `claude -p`
  (3 runs × 20 queries; a few % of the 5-hour plan window)
- `python3 scripts/package_skill.py` — build `dist/ste-explain.zip` for claude.ai upload
- `/eval [name]` — run all evals with-skill + baseline, grade, summarize
- `/hillclimb [n]` — n eval→diagnose→edit→re-eval climbs, logged
- `/lint <file>` — lint one file
- `/package` — package and print the three install routes

On Windows, use `python` where `python3` is not on PATH. The hook already
resolves this itself.

## Workflow: spec → eval → climb

1. Change `specs/skill-spec.md` deliberately, never as a side effect of an edit.
2. Never edit the skill without re-running `/eval`. Log every climb in
   `docs/hillclimb-log.md` (change, scores before/after).
3. Generalize from failures. The five evals are proxies for a million future
   prompts: if a fix only helps one eval, it is probably overfitting. Prefer
   explaining why over adding ALL-CAPS MUSTs.
4. Keep SKILL.md lean. For every line ask: would removing it cause failures?
   If not, cut it. Bloat makes the model ignore the rules that matter.
5. Use subagents for eval runs and reviews (fresh context, no bias toward
   text this session just wrote). The writer must not grade its own work.

## Hard rules

- NEVER copy text from the ASD-STE100 specification PDF. It is copyrighted.
  Distill in original wording and link to https://www.asd-ste100.org.
- The skill ships with zero scripts and zero dependencies, so it runs
  unchanged on claude.ai, Claude Code, and the API. Lint/eval tooling stays
  in `scripts/` and must never be referenced from SKILL.md.
- Frontmatter constraints (hook-enforced): name ≤64 chars, `[a-z0-9-]`, no
  "claude"/"anthropic"; description ≤1024 chars, single line; SKILL.md body
  ≤150 lines.
- The skill's own prose must pass `scripts/ste_lint.py` in description mode.
  A readability skill that is hard to read is dead on arrival.

## Repo etiquette

- Branch `main`; conventional commit subjects (feat:, fix:, docs:, eval:).
- `workspace/` and `dist/` are disposable and gitignored.
- Bump `version` in `.claude-plugin/plugin.json` on any user-visible change.
