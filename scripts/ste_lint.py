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
Errors: sentence over limit, paragraph over 6 sentences.
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
    "essentially", "basically", "arguably", "fundamentally", "notably",
    "importantly", "interestingly", "it is worth noting", "it should be noted",
    "needless to say", "of course", "clearly", "obviously", "quite",
    "somewhat", "fairly", "actually", "in fact",
    "as a matter of fact", "at the end of the day", "in order to",
    "prior to", "subsequent to", "utilize", "leverage", "facilitate",
    "commence", "approximately", "in the event that",
]

PASSIVE_RE = re.compile(
    r"\b(?:is|are|was|were|be|been|being|get|gets|got)\s+"
    r"(\w{2,}(?:ed|en|wn|ought|uilt)|\w{2,}ne)\b",
    re.IGNORECASE,
)
# Common adjectives/states that match the passive pattern but are not passive.
PASSIVE_ALLOW = {
    "open", "broken" , "done", "gone", "mistaken", "written",  # kept simple
    "closed", "based", "supposed", "used", "interested", "concerned",
    "allowed", "required", "unknown", "known",
}

FUNCTION_WORDS = {
    "a", "an", "the", "this", "that", "these", "those", "of", "to", "in",
    "on", "for", "with", "and", "or", "but", "if", "when", "then", "at",
    "by", "from", "as", "is", "are", "was", "were", "be", "it", "its",
    "you", "your", "we", "our", "they", "their", "not", "no", "do", "does",
    "can", "will", "must", "each", "every", "all", "any", "more", "most",
    "than", "into", "over", "under", "after", "before", "between", "use",
}

ING_ALLOW = {
    "thing", "things", "something", "anything", "everything", "nothing",
    "during", "morning", "evening", "string", "strings", "king", "ring",
    "spring", "wing", "sing", "being", "bring",
}

BULLET_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
HEADING_RE = re.compile(r"^\s*#{1,6}\s+")


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
    limit = PROCEDURE_LIMIT if procedure else DESCRIPTION_LIMIT
    errors, warnings = [], []

    # YAML frontmatter, fenced code blocks, and table rows are exempt.
    text = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.DOTALL)
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text = "\n".join(l for l in text.splitlines()
                     if not l.lstrip().startswith("|"))

    paragraphs = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    for pi, para in enumerate(paragraphs, 1):
        lines = para.splitlines()
        if not lines:
            continue
        is_list = any(BULLET_RE.match(l) for l in lines)
        if HEADING_RE.match(lines[0]):
            continue
        clean = " ".join(strip_markdown(BULLET_RE.sub("", l)) for l in lines)
        sentences = split_sentences(clean)

        if not is_list and len(sentences) > PARAGRAPH_LIMIT:
            errors.append(
                f"para {pi}: {len(sentences)} sentences (limit {PARAGRAPH_LIMIT})"
            )

        for sent in sentences:
            n = word_count(sent)
            if n > limit:
                errors.append(f"para {pi}: {n}-word sentence (limit {limit}): "
                              f"\"{sent[:60]}...\"")
            for m in PASSIVE_RE.finditer(sent):
                if m.group(1).lower() not in PASSIVE_ALLOW:
                    warnings.append(f"para {pi}: passive? \"{m.group(0)}\"")
            low = " " + sent.lower() + " "
            for h in HEDGES:
                if f" {h} " in low or low.strip().startswith(h + " "):
                    warnings.append(f"para {pi}: hedge/filler \"{h}\"")
            for span in noun_cluster_spans(sent):
                warnings.append(f"para {pi}: noun cluster? \"{span}\"")
        if ";" in clean:
            warnings.append(f"para {pi}: semicolon — write two sentences")

    all_words = re.findall(r"[A-Za-z'-]+", text)
    ing = [w for w in all_words
           if w.lower().endswith("ing") and w.lower() not in ING_ALLOW]
    if all_words and len(ing) / len(all_words) > 0.04:
        warnings.append(
            f"-ing density {len(ing)}/{len(all_words)} words — prefer simple verb forms"
        )

    return errors, warnings


def report(errors, warnings, as_json=False):
    if as_json:
        print(json.dumps({"errors": errors, "warnings": warnings,
                          "clean": not errors}, indent=2))
    else:
        for e in errors:
            print(f"ERROR   {e}")
        for w in warnings:
            print(f"warning {w}")
        print(f"\n{len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


def self_test():
    bad = ("The configuration of the system should essentially be performed "
           "by the administrator so that the comprehensive fare table "
           "validation reconciliation process can be initiated without "
           "further delay or additional manual intervention steps occurring.")
    good = ("Set the timer to 10 minutes. The pump starts when the timer "
            "ends. If the light is red, stop the test.")
    e1, w1 = lint_text(bad)
    assert e1, "expected a sentence-length error in the bad sample"
    assert any("passive" in w for w in w1), "expected a passive warning"
    assert any("hedge" in w for w in w1), "expected a hedge warning"
    assert any("noun cluster" in w for w in w1), "expected a noun-cluster warning"
    e2, w2 = lint_text(good, procedure=True)
    assert not e2, f"good sample should have no errors, got {e2}"
    assert not any("passive" in w for w in w2), f"false passive: {w2}"
    print("self-test PASS")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("file", nargs="?", help="file to lint")
    ap.add_argument("--text", help="lint a string instead of a file")
    ap.add_argument("--procedure", action="store_true",
                    help="use the 20-word instruction limit")
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
