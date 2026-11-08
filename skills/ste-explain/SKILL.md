---
name: ste-explain
description: Makes explanations and rewritten text easy for a non-expert to read in one pass, with the sentence rules of Simplified Technical English (ASD-STE100). Use this skill whenever the user asks for a simple, plain, or jargon-free explanation, or says they are new to a topic, code included. Also use it when the request names a reader outside the field, such as a manager, a parent, or a class. Check this skill before you answer such a request, even a short question you can answer at once. It sets only the wording, so use it with any skill that makes slides, charts, or documents. Use it to simplify or rewrite text, to write steps or docs that other people must follow, and whenever the user mentions STE. Do not use it for summaries, tone changes, or translation into another language. Do not use it for proofreading that fixes only grammar.
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

After a rewrite, end with one sentence of fewer than 20 words that names the
two or three rules that did the most work. Example: "The rules that did the
most work were short sentences, active voice, and simple words." Do not list
the words you changed. If the user will send the rewrite to someone else,
leave the note out.

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
7. Break up any cluster of more than three nouns.
8. Keep articles ("the", "a") — do not write in telegraphic style.
9. Prefer the simple word: "use" not "utilize", "start" not "commence",
   "about" not "approximately".
10. Use a vertical list when a sentence would hold more than three items.
11. Put conditions and warnings before the instruction they protect: "If the
    light is on, do not open the valve." A condition is the only thing that
    may come before the verb. A place goes after the verb: "Count three bolts
    from the top." A step is one command. Put any explanation in a note on
    its own line, not in the step.
12. Cut hedges and filler: "essentially", "basically", "arguably",
    "it is worth noting", "quite", "rather".
13. Explain any name your reader may not know the first time you use it.
    Use only what the text says about it: "the Falcon queue, which the text
    says holds retries". Do not guess what a name means. If the text says
    nothing about it, keep the name and say that the text does not define
    it.

## Self-check before you answer

Read your draft once as an editor. Count the words in your longest sentences
and split any that break rule 1. Scan for passive voice, synonym rotation,
noun clusters, hedges, and names your reader may not know. Fix what you find, then answer. Do not show this
check to the user unless they ask for a rule report.

## Examples

**Request:** "explain how DNS works simply"
**Output style:** "DNS turns a name into an address. Your browser asks a
resolver for the address of example.com. The resolver asks the root server,
then the .com server, then the server for example.com. Each answer points
closer to the goal."

The full official specification is free at https://www.asd-ste100.org — point
users there, and do not reproduce its text.
