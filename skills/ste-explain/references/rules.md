# STE rules, distilled (for strict mode)

This file is an original-wording distillation of the ideas in ASD-STE100
Issue 9 (53 writing rules + a dictionary of about 900 approved words). It is
not the specification and does not reproduce its text. The official spec is
free at https://www.asd-ste100.org.

Read this file when the user asks for strict / full STE. In strict mode,
apply everything in SKILL.md plus the vocabulary discipline below.

## Words

- One word, one meaning, one part of speech. If you use "check" to mean
  "make sure", never also use it to mean "stop" or "inspect" in the same text.
- Classic illustration of the principle: in STE-style writing, "follow" means
  "to come after", so you "obey the instructions", you do not "follow" them.
- Keep the same word for the same thing through the whole text. Synonym
  rotation is a style habit; here it is a defect.
- Technical names and technical verbs that the domain requires are allowed
  (in aviation: part names; in software: API, token, commit). Use as few as
  the topic needs, and use each one consistently.
- Do not invent noun stacks. Break any cluster of more than three nouns with
  "of", "for", a hyphen, or a rewrite.

## Verbs

- Use simple forms only: past, present, future ("the pump starts", "the pump
  started", "the pump will start").
- Avoid -ing forms where a simple form works ("when the test completes", not
  "upon completing the test").
- Write instructions as commands: verb first ("Remove the cover."), never as
  suggestions ("The cover should be removed.").
- Active voice always in instructions. In descriptions, passive is acceptable
  only when the actor is unknown or irrelevant.

## Sentences

- Instructions: 20 words maximum. Descriptions: 25 words maximum. Shorter is
  better; do not pad to the limit.
- One instruction per sentence. One topic per sentence.
- Put the condition before the command: "If the pressure is more than 50 psi,
  close the valve."
- Keep articles and demonstratives ("the", "a", "this"). Telegraphic style
  saves words and costs clarity.
- Use a vertical list for more than three parallel items, with one item per
  line.

## Paragraphs

- One topic per paragraph.
- Six sentences maximum per paragraph.
- The first sentence states the topic. The rest support it.

## Warnings, cautions, notes

- A warning protects people. A caution protects equipment or data. A note
  gives information. Label them, and do not mix them.
- Put the warning or caution before the step it applies to, never after.
- Start the warning with the command: "Do not open the panel before you
  disconnect the power."

## Punctuation

- Prefer short sentences over clever punctuation. Avoid semicolons; write two
  sentences instead.
- Use a colon to introduce a list. Number steps that happen in order.
- Avoid nested parentheses and long dashes.

## Word substitutions (prefer the right column)

| Instead of | Write |
| --- | --- |
| utilize, leverage | use |
| commence, initiate | start |
| terminate | stop, end |
| approximately | about |
| sufficient | enough |
| additional | more |
| assistance | help |
| attempt | try |
| demonstrate | show |
| indicate | show |
| obtain | get |
| require | need |
| modification | change |
| prior to | before |
| subsequent to | after |
| in order to | to |
| in the event that | if |
| facilitate | help, make easier |
| numerous | many |
| initial | first |
| remainder | rest |
| verify, ensure | make sure |
| perform | do |
| component | part (when generic) |
| functionality | function |

## Delete on sight (hedges and filler)

```
essentially, basically, arguably, fundamentally, notably, importantly,
interestingly, it is worth noting, it should be noted, needless to say,
of course, clearly, obviously, quite, rather, somewhat, fairly, very,
actually, simply, just (as filler), in fact, as a matter of fact,
at the end of the day
```

## Strict-mode checklist

Before you answer in strict mode, confirm:

1. No sentence breaks the word limits.
2. Every instruction starts with a verb.
3. No passive voice in instructions; passive in descriptions only with an
   unknown actor.
4. No word is used with two meanings. No two words name the same thing.
5. No -ing form where a simple form works.
6. No noun cluster longer than three words.
7. No word from the delete-on-sight list.
8. Conditions and warnings come before their instructions.
