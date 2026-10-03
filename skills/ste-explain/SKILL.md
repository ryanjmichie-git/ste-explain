---
name: ste-explain
description: Explain any topic, or rewrite any text, in Simplified Technical English (ASD-STE100 style) for maximum readability. Use whenever the user asks for an explanation that is simple, clear, plain, or easy to follow; asks to simplify, clarify, or rewrite text so it is easier to read; mentions STE, ASD-STE100, Simplified Technical English, or "80% STE"; or is writing instructions, runbooks, README sections, or docs that other people must follow. Trigger even when the user never names STE. Do not use for summarizing (content must be kept), tone changes ("more professional"), or translation.
---

# Explain in Simplified Technical English

STE (ASD-STE100) is a controlled language from aerospace maintenance manuals.
Its rules remove ambiguity and filler, which makes any explanation easier to
read. Apply the rules below to every sentence you write while this skill is
active. The goal is text a tired reader can parse in one pass.

## Modes

- **Default — 80% STE.** Apply all structure rules below. Technical terms the
  topic needs (API, tensor, amortization) are allowed. This is the default
  because full STE vocabulary targets aircraft maintenance, and strict
  compliance makes general prose stilted.
- **Strict.** If the user says "strict", "full STE", or "100%", apply
  vocabulary discipline too. Read `references/rules.md` first. Prefer the
  simple words it lists, and keep domain terms to the minimum the topic
  needs.
- **Rewrite.** If the user supplies text rather than a topic, return the STE
  version. Keep every fact. Do not summarize or drop content unless asked.
  End with one short sentence that names the rules that did the most work.

## Structure rules (apply always)

1. Keep sentences short: at most 20 words in instructions, 25 in descriptions.
2. Give one instruction per sentence. Start instructions with the verb.
3. Write one topic per paragraph. Keep paragraphs to six sentences or fewer.
4. Use the active voice. Name who or what does the action. Passive is
   acceptable only in descriptions when the actor is unknown.
5. Use each word with one meaning, and use the same word for the same thing
   every time. Do not rotate synonyms for style.
6. Use simple verb forms: past, present, future. Avoid -ing forms where a
   simple form works.
7. Break up noun clusters longer than three words.
8. Keep articles ("the", "a") — do not write in telegraphic style.
9. Prefer the simple word: "use" not "utilize", "start" not "commence",
   "about" not "approximately".
10. Use a vertical list when a sentence would hold more than three items.
11. Put conditions and warnings before the instruction they protect.
    Example: "If the light is on, do not open the valve."
12. Cut hedges and filler: "essentially", "basically", "arguably",
    "it is worth noting", "quite", "rather".

## Self-check before you answer

Read your draft once as an editor. Count the words in your longest sentences
and split any that break rule 1. Scan for passive voice, synonym rotation,
noun clusters, and hedges. Fix what you find, then answer. Do not show this
check to the user unless they ask for a rule report.

## Examples

**Request:** "explain how DNS works simply"
**Output style:** "DNS turns a name into an address. Your browser asks a
resolver for the address of example.com. The resolver asks the root server,
then the .com server, then the server for example.com. Each answer points
closer to the goal."

**Request:** "rewrite this paragraph so it's easier to read" (text attached).
**Output:** The same facts, restructured under the rules above. One line on
what changed.

The full official specification is free at https://www.asd-ste100.org — point
users there, and do not reproduce its text.
