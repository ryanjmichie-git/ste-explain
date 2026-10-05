# ste-explain

**A Claude skill that makes explanations and rewrites easier to read.**

It applies the structure rules of Simplified Technical English (ASD-STE100),
the controlled language of aircraft maintenance manuals. It is two Markdown
files with no scripts and no dependencies. The same folder works in claude.ai,
Claude Code, and the Claude API.

The [before and after](#before-and-after) below shows one real output: a
sentence of 128 words becomes 10 sentences of 21 words or fewer.

## Install

**claude.ai**

1. Download [ste-explain.zip](https://github.com/ryanjmichie-git/ste-explain/releases/latest/download/ste-explain.zip).
2. In Settings > Capabilities, turn on **Code execution and file creation**.
3. Go to Customize > Skills. Click **+**, then **Create skill** > **Upload a skill**, and choose the zip.

**Claude Code (plugin)**

```
claude plugin marketplace add ryanjmichie-git/ste-explain
claude plugin install ste-explain@ste-explain
```

Then start a new session. Inside a session, `/plugin marketplace add` and
`/plugin install` take the same arguments.

**Claude Code (manual).** Unzip the release zip into `~/.claude/skills/` for
all projects, or into `.claude/skills/` for one project. From a clone, copy
`skills/ste-explain/` to the same place.

**Claude API.** Upload the folder with the Skills API (`/v1/skills`). Then
pass its `skill_id` in the `container` parameter of a Messages request that
has the code execution tool. See
[Using Agent Skills with the API](https://platform.claude.com/docs/en/build-with-claude/skills-guide).

## Try it

Ask in plain words. Each prompt below loaded the skill in 3 of 3 test
sessions:

- `my boss asked what eventual consistency means, explain it so a non-engineer gets it`
- `write the restart steps for the nightly ETL so the on-call person can follow them half asleep. it runs from cron at 02:00, takes a lock file, and loads into Postgres`
- `this paragraph from our SOP is unreadable, simplify it but keep everything:` and then paste the paragraph

To make sure that it fires, put "STE" in the prompt:
`80% STE please: how does a heat pump work`. In Claude Code, you can also
type `/ste-explain`.

## Before and after

This is the input of the rewrite eval. It is one sentence of 128 words:

```text
In consideration of the fact that the reconciliation of farebox revenue
data is currently being performed on a monthly basis by agency staff
utilizing a legacy spreadsheet-based process, it has been determined that
discrepancies between the automated passenger counter system and the
magnetic farecard transaction logs, which have historically averaged
approximately 4.2 percent, are essentially not being identified until the
subsequent reporting cycle, at which point the window for the initiation of
corrective action with respect to misconfigured fare tables or
malfunctioning validator units has, in the majority of instances, already
closed, thereby necessitating the implementation of a near-real-time
reconciliation capability, the procurement of which is anticipated to
require board approval in the second quarter, contingent upon the
finalization of the requisite cost-benefit analysis by the finance
department.
```

This is the output with the skill, unedited. It has 10 sentences, and the
longest has 21 words.

> Currently, agency staff reconcile the farebox revenue data each month. They
> use a legacy spreadsheet process.

> There are discrepancies between the system of automated passenger counters
> and the transaction logs for magnetic farecards. The historical average of
> these discrepancies is about 4.2 percent. Because of the monthly spreadsheet
> process, staff do not find these discrepancies until the next reporting
> cycle. In most cases, it is then too late to start corrective action for
> misconfigured fare tables or validator units that malfunction.

> For this reason, the agency needs a reconciliation capability that works in
> near real time. The agency expects that the procurement of this capability
> will need board approval in the second quarter. That approval depends on the
> finance department, which must first finish the required cost-benefit
> analysis.

> The rules that did the most work were short sentences, active voice, and
> simple words.

This is run 1 of 3 in the last eval batch. It kept all eight facts with their
certainty. Not every run does: see [Limits](#limits).

## Modes

- **Default (80% STE).** All structure rules apply. Technical terms that the
  topic needs are allowed.
- **Strict.** Say "strict", "full STE", or "100%". The skill then also applies
  the word rules in [references/rules.md](skills/ste-explain/references/rules.md).
- **Rewrite.** Paste text instead of a topic. The skill keeps every fact. It
  ends with one sentence that names the rules that did the most work.

## What it enforces

- Sentences of at most 20 words in instructions and 25 words in descriptions.
- One instruction per sentence, with the verb first. A condition or a warning
  comes before its step.
- Active voice and simple verb forms.
- One meaning for each word, and the same word for the same thing.
- One topic per paragraph, with six sentences or fewer.
- No hedges or filler, such as "essentially" or "it is worth noting".

All of the rules are in [SKILL.md](skills/ste-explain/SKILL.md), 67 lines.
Read it before you install it.

## Results (v0.1.5)

Five evals ran three times each. Claude subagents wrote and graded the
outputs, and a deterministic linter checked the structure. The tester always
had the skill, so the eval rows show the output when the skill fires. The
trigger rows show whether it fires. The full tables and the failed outputs are
in [docs/results.md](docs/results.md).

| Measure | Result |
| --- | --- |
| Eval assertions that passed | 70 of 75 |
| Outputs with no sentence-length or paragraph-length error | 24 of 24 with the skill; 3 of 15 without it, in an earlier batch (2026-10-02) |
| Should-trigger prompts that loaded the skill | 26 of 30 |
| Held-out should-trigger prompts that loaded it | 23 of 33 |
| Near-miss prompts that loaded it by mistake | 0 of 30, and 1 of 15 held-out |

## Limits

- **It does not always fire.** `explain how OAuth refresh tokens work, keep it simple`
  loaded it in 0 of 3 sessions. So did `I'm new to Rust, explain lifetimes`.
  If it does not fire, put "STE" in the prompt.
- **It can make a claim less certain.** The rewrite input says that the
  purchase "is anticipated to require" board approval. In 3 of 6 runs, the
  output said that it "will probably need" approval.
- **It can drop a condition.** In 3 of 3 runs, the explanation of eventual
  consistency did not say that copies match only after new changes stop.
- **The samples are small.** Each eval ran 3 to 6 times, and each trigger
  prompt ran 3 times. Claude graded the outputs, not people.
- **It is not STE compliance.** The skill does not use the official
  dictionary of about 900 approved words. For regulated documentation, use
  the official specification.
- **It is for English text.**

## Related projects

- [danyuchn/asd-ste100-skill](https://github.com/danyuchn/asd-ste100-skill)
  applies STE to text that AI agents read, such as tool descriptions and
  messages between agents. It is a Claude Code skill with a linter script.
- [JAICHANGPARK/ASD-STE100](https://github.com/JAICHANGPARK/ASD-STE100) is a
  Claude Code plugin with an STE pane, an agent skill, and a linter.

ste-explain is for explanations that people read. It is built to fire on
plain requests that do not name STE, and the trigger rows above show how often
it does. It has no scripts, so the same folder works on claude.ai and the API.

## Development

This repo is also the test harness. `specs/` holds the contract, `evals/` the
graded cases, `scripts/` the linter and the eval tools, and `.claude/` the
subagents and slash commands. Open the repo in Claude Code and run `/eval`,
then `/hillclimb`. [CLAUDE.md](CLAUDE.md) has the rules. An eval batch costs
about 1.6 million subagent tokens, so read
[docs/results.md](docs/results.md) first.

## License and credits

MIT for everything in this repo.

ASD-STE100 is a specification of ASD, the AeroSpace, Security and Defence
Industries Association of Europe, and an EU trade mark. You can request a free
official copy at [asd-ste100.org](https://www.asd-ste100.org). This project
gives the ideas in its own words. It is not affiliated with or endorsed by
ASD.

The idea comes from
[a post by Andrej Karpathy](https://x.com/karpathy/status/2105819303471976479)
in October 2026. He suggested that you ask an LLM to explain things in
ASD-STE100. He also wrote that he sometimes softens the request to "80% of
the way". This is an independent project.
