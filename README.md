# ste-explain

**A Claude skill for text that other people will read: explanations, rewrites, and instructions.**

It applies the structure rules of Simplified Technical English (ASD-STE100),
the controlled language of aircraft maintenance manuals. It is two Markdown
files with no scripts and no dependencies. It makes no network calls and
stores no data. The same folder works in claude.ai, Claude Code, and the
Claude API. It is not meant to change how Claude writes in every message.

The [before and after](#before-and-after) below shows one real output: a
paragraph of 94 words about a phone data plan becomes six short sentences.

## Install

**claude.ai (plugin)**

1. Go to Customize > Plugins and add the marketplace
   `ryanjmichie-git/ste-explain`.
2. Install **ste-explain** from it, then start a new chat.

This route was checked on 2026-10-07. The prompt "my boss asked what
eventual consistency means, explain it so a non-engineer gets it" loaded the
skill.

**claude.ai (zip, if the plugin route is not available to you)**

1. Download [ste-explain.zip](https://github.com/ryanjmichie-git/ste-explain/releases/latest/download/ste-explain.zip).
2. In Settings > Capabilities, turn on **Code execution and file creation**.
3. Go to Customize > Skills. Click **+**, then **Create skill** > **Upload a skill**, and choose the zip.

**Claude Code (plugin)**

```
claude plugin marketplace add ryanjmichie-git/ste-explain
claude plugin install ste-explain@ste-explain
```

Then start a new session. Inside a session, `/plugin marketplace add` and
`/plugin install` take the same arguments. The plugin runs no code.
`scripts/`, `evals/` and `.claude/` are development tools that installing
the plugin does not load.

**Claude Code (manual).** Unzip the release zip into `~/.claude/skills/` for
all projects, or into `.claude/skills/` for one project. From a clone, copy
`skills/ste-explain/` to the same place.

**Claude API.** Upload the folder with the Skills API (`/v1/skills`). Then
pass its `skill_id` in the `container` parameter of a Messages request that
has the code execution tool. See
[Using Agent Skills with the API](https://platform.claude.com/docs/en/build-with-claude/skills-guide).
This route was checked on 2026-10-07 with the Python SDK: the upload, then
one call with the code execution tool. The reply had 0 lint errors.

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

This test input is one paragraph of 94 words and 3 sentences:

```text
Once the monthly high-speed data allowance of 20 GB has been fully consumed,
data speeds will be reduced to a maximum of 128 kbps for the remainder of
the billing cycle, a rate which is generally sufficient for messaging and
email but insufficient for video streaming. Unused high-speed data is not
carried over into the following month. Additional high-speed data may be
purchased at any time in increments of 5 GB, although such purchases expire
at the end of the billing cycle in which they were made, irrespective of
whether they have been used.
```

The prompt was `this paragraph is hard to read, simplify it but keep everything:` and
then the paragraph. This is the output with the skill, unedited:

<blockquote>

You get 20 GB of high-speed data each month. When you use all 20 GB, your speed drops to a maximum of 128 kbps for the rest of the billing cycle. That speed is usually enough for messaging and email, but not for video streaming.

High-speed data that you do not use does not carry over to the next month.

You can buy more high-speed data at any time, in 5 GB blocks. Each block expires at the end of the billing cycle in which you bought it, even if you did not use it.

Most of the work came from the active voice, one idea per sentence, and cutting the long passive clauses ("has been fully consumed", "irrespective of whether they have been used") into plain statements.

</blockquote>

The output kept every fact and qualifier. The body has six sentences, and the
longest has 22 words. The closing note has 33 words, over the skill's own
limit of 25. This is one of twelve test inputs that each ran once. Four of
the twelve kept every fact and qualifier, as
[docs/results.md](https://github.com/ryanjmichie-git/ste-explain/blob/main/docs/results.md#before-and-after-picks) shows.

<details>
<summary>A longer example from the eval set (128 words)</summary>

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

</details>

## Modes

- **Default (80% STE).** All structure rules apply. Technical terms that the
  topic needs are allowed.
- **Strict.** Say "strict", "full STE", or "100%". The skill then also applies
  the word rules in [references/rules.md](https://github.com/ryanjmichie-git/ste-explain/blob/main/skills/ste-explain/references/rules.md).
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
- Names the reader may not know are explained from the text the first
  time, or marked as undefined. No guessed meanings.

All of the rules are in [SKILL.md](https://github.com/ryanjmichie-git/ste-explain/blob/main/skills/ste-explain/SKILL.md), 72 lines.
Read it before you install it.

## Use the rules inside your own skills

A skill that does a task fires every time you run that task. Put the
structure rules in that skill, and its text follows them with no separate
trigger. Good candidates are skills that post release notes or Slack updates,
or that write runbooks and pull request descriptions. Copy the twelve rules
from the [structure rules](https://github.com/ryanjmichie-git/ste-explain/blob/main/skills/ste-explain/SKILL.md#structure-rules-apply-always)
in SKILL.md. The MIT license allows it.

This pattern comes from user feedback. One user keeps style rules in a skill
that posts to Slack, and Claude follows them every time with no reminder.
This repo does not measure it.

## Results (v0.1.5)

Five evals ran three times each. Claude subagents wrote and graded the
outputs, and a deterministic linter checked the structure. The tester always
had the skill, so the eval rows show the output when the skill fires. The
trigger rows show whether it fires. The full tables and the failed outputs are
in [docs/results.md](https://github.com/ryanjmichie-git/ste-explain/blob/main/docs/results.md).

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
- **It is tested only in short, fresh sessions.** One user reports that it
  does not hold in long engineering sessions or after the context is
  compacted. There, Claude kept using names that it had made up.
- **It turns advice into a command.** "It is recommended that..." became a
  direct command in 4 of 4 test inputs that held a recommendation.
- **Its closing note runs long.** In rewrite mode, the note broke the 25-word
  limit in 6 of 11 rewrites.
- **The samples are small.** Each eval ran 3 to 6 times, and each trigger
  prompt ran 3 times. Claude graded the outputs, not people.
- **It is not STE compliance.** The skill does not use the official
  dictionary of about 900 approved words. For regulated documentation, use
  the official specification.
- **It is for English text.**

## FAQ

**Why not just ask Claude to simplify?** For a one-off, a follow-up prompt
works. One user asks "can you restate that in concise, non-technical terms
please?" and is happy with the result. We tested that prompt against the
skill on 2026-10-06.

Three arms ran the five eval prompts three times each: plain Claude, plain
Claude and then the follow-up, and the skill. Blind graders counted the
checks passed, 72 per arm. The method and the failed outputs are in
[docs/results.md](https://github.com/ryanjmichie-git/ste-explain/blob/main/docs/results.md#against-a-follow-up-prompt-iteration-17).

| Arm | Checks passed | Outputs with no lint error | Turns |
| --- | --- | --- | --- |
| Plain Claude | 38 of 72 | 0 of 15 | 1 |
| Plain Claude, then the follow-up | 27 of 72 | 3 of 15 | 2 |
| The skill, first answer | 52 of 72 | 8 of 15 | 1 |

The follow-up made the text easier to read, but it removed facts. The
runbooks lost the cron job, the lock file path and Postgres in 3 of 3 runs,
and "4.2 percent" became "about 4 percent". The skill kept the terms and the
sentence limit in one turn. It is not perfect either: it passed 52 of 72
checks, not 72.

## Related projects

- [obra/the-elements-of-style](https://github.com/obra/the-elements-of-style)
  packages Strunk's text of 1918, with its 18 rules, as a reference of about
  12,000 tokens. Claude reads it when it writes prose. STE differs in that
  it adds countable limits that a linter can check. ste-explain costs about
  180 tokens in every session and about 790 more when it fires.
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
then `/hillclimb`. [CLAUDE.md](https://github.com/ryanjmichie-git/ste-explain/blob/main/CLAUDE.md) has the rules. An eval batch costs
about 1.6 million subagent tokens, so read
[docs/results.md](https://github.com/ryanjmichie-git/ste-explain/blob/main/docs/results.md) first.

## Support

Report a problem or a security problem in [GitHub Issues](https://github.com/ryanjmichie-git/ste-explain/issues).

## License and credits

MIT for everything in this repo.

ASD-STE100 is a specification of ASD, the AeroSpace, Security and Defence
Industries Association of Europe, and an EU trade mark. You can request a free
official copy at [asd-ste100.org](https://www.asd-ste100.org). This project
gives the ideas in its own words. It is not affiliated with or endorsed by
ASD.

This project started from
[a post by Andrej Karpathy](https://x.com/karpathy/status/2105819303471976479)
in October 2026. He suggested that you ask an LLM to explain things in
ASD-STE100. He also wrote that he sometimes softens the request to "80% of
the way". STE itself dates from the late 1970s. See
[asd-ste100.org](https://www.asd-ste100.org). This is an independent
project.
