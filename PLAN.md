# Plan: ste-explain

A downloadable Claude Skill that makes model output easier to read by
applying ASD-STE100 (Simplified Technical English), softened to Karpathy's
"80% of the way" default.

## Why

Karpathy ([Oct 1, 2026 post](https://x.com/karpathy/status/2105819303471976479)):
as AI does more of the work, our job shifts to reading its output. Asking the
model to write in ASD-STE100 makes output "a lot more readable"; he softens
the request to "80% of the way" because the full spec is stringent. STE
(maintained by ASD, Issue 9, Jan 2025, free but copyrighted) has 53 writing
rules and a ~900-word dictionary; the structural rules — ≤20/25-word
sentences, active voice, one meaning per word — are what transfer to general
explanations.

## Differentiator

Prior art exists (JAICHANGPARK/ASD-STE100, danyuchn/asd-ste100-skill, and
others) — mostly Claude Code plugins with linters and slash commands. This
skill competes on radical ease of use: one dependency-free SKILL.md +
references file that runs unchanged on claude.ai (zip upload), Claude Code
(plugin or folder copy), and the API, and triggers on plain requests
("explain this simply") — not only when someone types "ASD-STE100".

## Deliverable layout

- `skills/ste-explain/` — the product (SKILL.md, references/rules.md)
- `specs/` — behavior contract and measurable success criteria
- `evals/` — 5 graded eval cases + 20 trigger-eval queries + fixtures
- `scripts/` — deterministic verifiers (ste_lint, validate_skill, package)
- `.claude/` — dev harness: subagents (tester, baseline, grader, red-team),
  slash commands (/eval, /hillclimb, /lint, /package), PostToolUse hook
- `.claude-plugin/` — plugin + marketplace manifests for one-command install

## Phases

1. **Scaffold** — this repo. Done.
2. **Hill-climb** — in Claude Code: run `/eval`, review in the viewer or the
   summary table, `/hillclimb` until `specs/success-criteria.md` passes.
   Expect most of the session here.
3. **Trigger tuning** — run the trigger evals; harden the description against
   the near-miss negatives (summarize ≠ simplify, tone ≠ clarity).
4. **Publish** — push to github.com/ryanjmichie-git/ste-explain, attach
   `dist/ste-explain.zip` to a release, verify all three install routes from
   a clean machine.
5. **v2 candidates (only if v1 gets traction)** — linter script shipped with
   the skill, /ste slash command, diagram-mode companion (Karpathy's other
   tips). Each breaks "one file, works everywhere", so they wait.

## Best practices built in, and where they came from

- **Karpathy** ([the post](https://x.com/karpathy/status/2105819303471976479)):
  the 80% default; lean prompts that explain why instead of stacking MUSTs;
  generalize from eval failures instead of overfitting (encoded in CLAUDE.md
  and /hillclimb).
- **Boris Cherny** ([Claude Code best practices](https://code.claude.com/docs/en/best-practices)):
  give Claude a check it can run (ste_lint + grader close the loop without a
  human); explore → plan → code (this PLAN.md, plan mode for big edits); keep
  CLAUDE.md short enough that every line earns its place; hooks for rules
  that must hold every time (frontmatter validation); fresh-context
  adversarial review before calling work done (red-team-reviewer agent).
- **Daisy Hollman** ([Agentic Software Engineering at Scale](https://daily.dev/posts/how-anthropic-uses-claude-code-agentic-software-engineering-at-scale---daisy-hollman-lwzdz8jka)):
  context is the fundamental primitive — the skill is a lazy prompt
  (references load only in strict mode), hooks inject feedback only when
  relevant, and eval runs happen in subagents so the parent context stays
  small; scale climbs across parallel sessions/worktrees when iterating hard.

## Sources

- Karpathy on X: https://x.com/karpathy/status/2105819303471976479
- ASD-STE100 official: https://www.asd-ste100.org (spec free; do not copy text)
- STE overview: https://en.wikipedia.org/wiki/Simplified_Technical_English
- Agent Skills docs: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- Claude Code best practices: https://code.claude.com/docs/en/best-practices
- Plugins overview: https://code.claude.com/docs/en/plugins
