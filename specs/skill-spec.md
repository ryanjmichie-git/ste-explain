# Skill spec: ste-explain

This is the behavior contract. The skill passes when its output satisfies
this file on realistic prompts, not when it merely sounds simple. Change
this file deliberately; never bend it to excuse a failing eval.

## Purpose

Given a topic to explain or a text to rewrite, produce prose that follows
the structural rules of ASD-STE100 at Karpathy's pragmatic "80%" level by
default, so that a tired reader can parse it in one pass.

## Modes

| Mode | Trigger | Behavior |
| --- | --- | --- |
| Default (80%) | any triggering request | structure rules enforced; technical terms the topic needs are allowed |
| Strict | user says "strict", "full STE", "100%" | also read references/rules.md; vocabulary discipline; minimum domain terms |
| Rewrite | user supplies text instead of a topic | STE version of the same content; every fact kept; no summarizing; one-line change note |

## Trigger contract

Must trigger on: simple/plain/clear explanation requests; simplify or
rewrite-for-readability requests; any mention of STE, ASD-STE100,
Simplified Technical English; writing instructions, runbooks, or docs that
others must follow.

Must NOT trigger on: summarization ("summarize", "TL;DR", "in two
sentences"); tone changes ("more professional", "more persuasive");
translation; proofreading for grammar only.

## Output rules (the testable core)

1. Sentence length: ≤20 words in instructions, ≤25 in descriptions.
2. Instructions: one per sentence, verb first, imperative.
3. Paragraphs: one topic, ≤6 sentences.
4. Active voice; passive only in descriptions with an unknown actor.
5. One meaning per word; one word per thing; no synonym rotation.
6. Simple verb forms; minimal -ing forms.
7. No noun clusters over three words.
8. Articles kept; no telegraphic style.
9. Vertical lists for more than three parallel items.
10. Conditions and warnings before their instructions.
11. No hedge/filler words (list in references/rules.md).
12. Rewrite mode preserves every fact of the source.
13. Names the stated reader may not know are explained on first use from
    what the source says. No guessed meanings; a name the source does not
    define is marked as undefined.

## Quality bar beyond the rules

Rule-passing text can still be bad. The output must also be correct,
complete for the question asked, and natural enough that a reader does not
notice the constraint — the reader should notice only that it is easy to
read.

## Non-goals (v1)

No linter shipped with the skill. No slash command. No diagrams/HTML/video
modes. No reproduction of spec text. No dependencies of any kind inside
`skills/ste-explain/`.

## Constraints

- Cross-surface purity: the skill folder must work unchanged on claude.ai,
  Claude Code, and the API.
- Frontmatter: name ≤64 chars `[a-z0-9-]`, no "claude"/"anthropic";
  description ≤1024 chars, single line, states what + when + when-not.
- SKILL.md body ≤150 lines; references/rules.md ≤200 lines.
