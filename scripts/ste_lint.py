#!/usr/bin/env python3
"""Deterministic STE structure checks.

Heuristic by design: it catches the violations that matter most (sentence
length, paragraph length, passive voice, hedges, noun clusters, -ing
density). It is not a full ASD-STE100 checker and does not try to be.

Usage:
  python3 scripts/ste_lint.py FILE [--procedure] [--json]
  python3 scripts/ste_lint.py --text "Some text." [--procedure]
  python3 scripts/ste_lint.py --self-test

Exit codes: 0 clean, 1 errors found, 2 usage problem.
Errors: sentence over limit, paragraph over 6 sentences. With --procedure,
steps and warning commands take 20 words; notes and prose take 25.
Warnings: passive voice, hedges, -ing density, noun clusters, semicolons.
"""

import argparse
import json
import re
import sys

DESCRIPTION_LIMIT = 25
PROCEDURE_LIMIT = 20
PARAGRAPH_LIMIT = 6

HEDGES = [
    "essentially",
    "basically",
    "arguably",
    "fundamentally",
    "notably",
    "importantly",
    "interestingly",
    "it is worth noting",
    "it should be noted",
    "needless to say",
    "of course",
    "clearly",
    "obviously",
    "quite",
    "somewhat",
    "fairly",
    "actually",
    "in fact",
    "as a matter of fact",
    "at the end of the day",
    "in order to",
    "prior to",
    "subsequent to",
    "utilize",
    "leverage",
    "facilitate",
    "commence",
    "approximately",
    "in the event that",
    "rather",
    "very",
    "simply",
    "just",
]

PASSIVE_RE = re.compile(
    r"\b(?:is|are|was|were|be|been|being|get|gets|got)\s+"
    r"(\w{2,}(?:ed|en|wn|ought|uilt)|\w{2,}ne)\b",
    re.IGNORECASE,
)
# Common adjectives/states that match the passive pattern but are not passive.
PASSIVE_ALLOW = {
    "open",
    "broken",
    "done",
    "gone",
    "mistaken",  # kept simple
    "closed",
    "based",
    "supposed",
    "used",
    "interested",
    "concerned",
    "allowed",
    "required",
    "unknown",
    "known",
    # -en adverbs/prepositions, not participles.
    "when",
    "then",
    "often",
    "even",
    "between",
}

FUNCTION_WORDS = {
    "a",
    "an",
    "the",
    "this",
    "that",
    "these",
    "those",
    "of",
    "to",
    "in",
    "on",
    "for",
    "with",
    "and",
    "or",
    "but",
    "if",
    "when",
    "then",
    "at",
    "by",
    "from",
    "as",
    "is",
    "are",
    "was",
    "were",
    "be",
    "it",
    "its",
    "you",
    "your",
    "we",
    "our",
    "they",
    "their",
    "not",
    "no",
    "do",
    "does",
    "can",
    "will",
    "must",
    "each",
    "every",
    "all",
    "any",
    "more",
    "most",
    "than",
    "into",
    "over",
    "under",
    "after",
    "before",
    "between",
    "use",
}

ING_ALLOW = {
    "thing",
    "things",
    "something",
    "anything",
    "everything",
    "nothing",
    "during",
    "morning",
    "evening",
    "string",
    "strings",
    "king",
    "ring",
    "spring",
    "wing",
    "sing",
    "being",
    "bring",
}

BULLET_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
HEADING_RE = re.compile(r"^\s*#{1,6}\s+")
LABEL_RE = re.compile(r"^(note|tip|warning|caution|important)\s*:\s*", re.IGNORECASE)
NOTE_LABELS = {"note", "tip"}


def strip_markdown(line: str) -> str:
    line = re.sub(r"`[^`]*`", "CODE", line)
    line = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", line)
    line = re.sub(r"[*_]{1,3}([^*_]+)[*_]{1,3}", r"\1", line)
    return line


def split_sentences(text: str):
    text = re.sub(r"\b(e\.g|i\.e|etc|vs|Mr|Ms|Dr|No)\.", r"\1<DOT>", text)
    parts = re.split(r"(?<=[.!?])\s+|(?<=[.!?][\"'\)\]])\s+", text)
    return [p.replace("<DOT>", ".").strip() for p in parts if p.strip()]


def word_count(sentence: str) -> int:
    return len(re.findall(r"[A-Za-z0-9'’-]+", sentence))


def noun_cluster_spans(sentence: str):
    tokens = re.findall(r"[A-Za-z][A-Za-z'-]*", sentence)
    spans, run = [], []
    for tok in tokens:
        if tok.lower() in FUNCTION_WORDS or len(tok) <= 2:
            if len(run) >= 4:
                spans.append(" ".join(run))
            run = []
        else:
            run.append(tok)
    if len(run) >= 4:
        spans.append(" ".join(run))
    return spans


def lint_text(text: str, procedure: bool = False):
    errors, warnings = [], []

    # YAML frontmatter, fenced code blocks, and table rows are exempt.
    text = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.DOTALL)
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text = "\n".join(l for l in text.splitlines() if not l.lstrip().startswith("|"))

    # --procedure: a step (list item) and the command sentence of a Warning
    # or Caution take the 20-word limit. A note, a reason after a warning
    # command, and prose around the list are descriptions and take 25. Text
    # with no list at all is treated as instructions throughout.
    has_list = any(BULLET_RE.match(l) for l in text.splitlines())

    paragraphs = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    for pi, para in enumerate(paragraphs, 1):
        lines = para.splitlines()
        if not lines:
            continue
        is_list = any(BULLET_RE.match(l) for l in lines)
        if HEADING_RE.match(lines[0]):
            continue
        # Each unit is [text, limit of its first sentence, limit of the rest].
        # In a list, each bullet starts a new unit, so a ":" lead-in or an
        # unpunctuated item does not merge with the next item. A labelled
        # line (Note:, Warning:) also starts a unit. Wrapped continuation
        # lines stay with their unit.
        units = []
        for l in lines:
            is_bullet = bool(BULLET_RE.match(l))
            seg = strip_markdown(BULLET_RE.sub("", l)).strip()
            seg = re.sub(r"^>\s*", "", seg)
            label = LABEL_RE.match(seg)
            if label:
                seg = seg[label.end() :]
            if not units or label or (is_list and is_bullet):
                if not procedure:
                    first = rest = DESCRIPTION_LIMIT
                elif label:
                    is_note = label.group(1).lower() in NOTE_LABELS
                    first = DESCRIPTION_LIMIT if is_note else PROCEDURE_LIMIT
                    rest = DESCRIPTION_LIMIT
                elif is_bullet or not has_list:
                    first = rest = PROCEDURE_LIMIT
                else:
                    first = rest = DESCRIPTION_LIMIT
                units.append([seg, first, rest])
            else:
                units[-1][0] += " " + seg
        clean = " ".join(u[0] for u in units)
        sentences = [
            (s, u[1] if i == 0 else u[2])
            for u in units
            for i, s in enumerate(split_sentences(u[0]))
        ]

        if not is_list and len(sentences) > PARAGRAPH_LIMIT:
            errors.append(
                f"para {pi}: {len(sentences)} sentences (limit {PARAGRAPH_LIMIT})"
            )

        for sent, limit in sentences:
            n = word_count(sent)
            if n > limit:
                errors.append(
                    f'para {pi}: {n}-word sentence (limit {limit}): "{sent[:60]}..."'
                )
            for m in PASSIVE_RE.finditer(sent):
                if m.group(1).lower() not in PASSIVE_ALLOW:
                    warnings.append(f'para {pi}: passive? "{m.group(0)}"')
            low = " " + sent.lower().replace("rather than", "") + " "
            for h in HEDGES:
                if f" {h} " in low or low.strip().startswith(h + " "):
                    warnings.append(f'para {pi}: hedge/filler "{h}"')
            for span in noun_cluster_spans(sent):
                warnings.append(f'para {pi}: noun cluster? "{span}"')
        if ";" in clean:
            warnings.append(f"para {pi}: semicolon — write two sentences")

    all_words = re.findall(r"[A-Za-z'-]+", text)
    ing = [
        w for w in all_words if w.lower().endswith("ing") and w.lower() not in ING_ALLOW
    ]
    if all_words and len(ing) / len(all_words) > 0.04:
        warnings.append(
            f"-ing density {len(ing)}/{len(all_words)} words — prefer simple verb forms"
        )

    return errors, warnings


def report(errors, warnings, as_json=False):
    if as_json:
        print(
            json.dumps(
                {"errors": errors, "warnings": warnings, "clean": not errors}, indent=2
            )
        )
    else:
        for e in errors:
            print(f"ERROR   {e}")
        for w in warnings:
            print(f"warning {w}")
        print(f"\n{len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


def self_test():
    bad = (
        "The configuration of the system should essentially be performed "
        "by the administrator so that the comprehensive fare table "
        "validation reconciliation process can be initiated without "
        "further delay or additional manual intervention steps occurring."
    )
    good = (
        "Set the timer to 10 minutes. The pump starts when the timer "
        "ends. If the light is red, stop the test."
    )
    e1, w1 = lint_text(bad)
    assert e1, "expected a sentence-length error in the bad sample"
    assert any("passive" in w for w in w1), "expected a passive warning"
    assert any("hedge" in w for w in w1), "expected a hedge warning"
    assert any("noun cluster" in w for w in w1), "expected a noun-cluster warning"
    e2, w2 = lint_text(good, procedure=True)
    assert not e2, f"good sample should have no errors, got {e2}"
    assert not any("passive" in w for w in w2), f"false passive: {w2}"
    # Lists: each bullet is its own unit; continuation lines stay joined.
    substep = (
        "6. If the old chain has a quick link, open it:\n"
        "   1. Put the tips of the quick-link pliers into the two links "
        "next to the quick link."
    )
    e3, _ = lint_text(substep, procedure=True)
    assert not e3, f"lead-in merged with sub-step: {e3}"
    tools = (
        "You need these tools:\n- Bicycle repair stand\n- Chain tool\n"
        "- Quick-link pliers\n"
        "- New chain for the same number of rear sprockets\n"
        "- Quick link for the new chain\n- Clean cloth\n- Gloves"
    )
    e4, _ = lint_text(tools, procedure=True)
    assert not e4, f"unpunctuated list merged: {e4}"
    long_item = (
        "- Wear gloves.\n- Turn the handle of the chain tool slowly in "
        "the clockwise direction until the pin of the tool pushes the "
        "rivet fully out of the chain."
    )
    e5, _ = lint_text(long_item, procedure=True)
    assert e5, "a long list item must still be an error"
    wrapped = (
        "1. Turn the handle of the chain tool slowly in the clockwise\n"
        "   direction until the pin of the tool pushes the rivet fully\n"
        "   out of the chain.\n2. Remove the chain."
    )
    e6, _ = lint_text(wrapped, procedure=True)
    assert any("26-word" in e for e in e6), f"continuation not joined: {e6}"
    _, w7 = lint_text("The risk is when the job hangs. The log is often empty.")
    assert not any("passive" in w for w in w7), f"false passive: {w7}"
    _, w8 = lint_text("It was written by the old team.")
    assert any("passive" in w for w in w8), "expected passive for 'was written'"
    _, w9 = lint_text("Use the tool rather than your hands. The tool is very slow.")
    assert any('hedge/filler "very"' in w for w in w9), f"missed 'very': {w9}"
    assert not any('"rather"' in w for w in w9), f"'rather than' flagged: {w9}"
    # Procedure mode: a step and the command of a warning take 20 words. A
    # note, a reason after a warning command, and prose around a list take 25.
    s22 = (
        "Turn the handle of the chain tool slowly until the pin of the tool "
        "pushes the rivet fully out of the chain."
    )
    n25 = (
        "The new chain and its quick link must have the same number of links "
        "as the old chain before you removed it from the bicycle."
    )

    def errs(text, procedure=True):
        return lint_text(text, procedure=procedure)[0]

    assert any(
        "22-word sentence (limit 20)" in e for e in errs("1. Wear gloves.\n2. " + s22)
    ), "a 22-word step must be an error"
    assert not errs("1. Wear gloves.\n\n   **Note:** " + s22), "note after a blank line"
    assert not errs("1. Count the links.\n   Note: " + n25), "label counted as a word"
    wrapped_note = (
        "1. Count the links.\n   Note: The new chain and its quick link must "
        "have the same number\n   of links as the old chain before you removed "
        "it from the bicycle again."
    )
    assert any("26-word sentence (limit 25)" in e for e in errs(wrapped_note))
    assert any(
        "(limit 20)" in e for e in errs("**WARNING:** " + s22 + "\n\n1. Wear gloves.")
    ), "the command of a warning takes 20"
    own_unit = (
        "1. Remove the old chain from the rear derailleur\n"
        "   Note: You need the old chain later to count the number of links in it"
    )
    assert not errs(own_unit), "a note line must not merge into its step"
    assert not errs("> **NOTE:** " + s22 + "\n\n1. Wear gloves."), "blockquote note"
    lead_in = (
        "Before you start, make sure that you have all of the tools in this "
        "list and a clean place to work:\n- Chain tool\n- Gloves"
    )
    assert not errs(lead_in), "lead-in prose before a list is a description"
    assert not errs("Warning: Wear gloves. " + s22 + "\n\n1. Remove the chain."), (
        "a reason after a warning command is a description"
    )
    assert any("(limit 20)" in e for e in errs(s22)), "no list: all instructions"
    assert not errs("1. Wear gloves.\n2. " + s22, procedure=False)
    print("self-test PASS")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("file", nargs="?", help="file to lint")
    ap.add_argument("--text", help="lint a string instead of a file")
    ap.add_argument(
        "--procedure",
        action="store_true",
        help="20-word limit for steps and warnings, 25 for notes and prose",
    )
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        sys.exit(self_test())
    if args.text is not None:
        text = args.text
    elif args.file:
        with open(args.file, encoding="utf-8") as f:
            text = f.read()
    else:
        ap.print_help()
        sys.exit(2)

    errors, warnings = lint_text(text, procedure=args.procedure)
    sys.exit(report(errors, warnings, as_json=args.json))


if __name__ == "__main__":
    main()
