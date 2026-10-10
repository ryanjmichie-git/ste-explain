#!/usr/bin/env python3
"""Check that the README, manifest, spec, eval and skill agree with each other.

Checks (one line of output each, "ok" or "FAIL"):
  C1  README's "Copy the <N> rules" matches the numbered rules in SKILL.md
  C2  README's "SKILL.md ..., N lines" matches the file's line count
  C3  plugin.json and marketplace.json share one description, with no
      "every fact" promise, and the description passes the linter
  C4  SKILL.md, rules.md, the spec and the eval all count noun clusters in
      nouns, never in words
  C5  SKILL.md and rules.md pass ste_lint in description mode

Usage: python3 scripts/check_consistency.py [repo_root]
Exit codes: 0 all ok, 1 a check failed.
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ste_lint import lint_text  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
FILES = (
    "skills/ste-explain/SKILL.md",
    "skills/ste-explain/references/rules.md",
    "README.md",
    ".claude-plugin/plugin.json",
    ".claude-plugin/marketplace.json",
    "specs/skill-spec.md",
    "evals/evals.json",
)
NUMBER_WORDS = {
    w: i + 1
    for i, w in enumerate(
        "one two three four five six seven eight nine ten eleven twelve "
        "thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty".split()
    )
}


def rule_count(skill_text: str) -> int:
    """Numbered items between the Structure rules heading and the next heading."""
    section = re.search(
        r"^## Structure rules.*?$(.*?)(?=^## |\Z)", skill_text, re.S | re.M
    )
    if not section:
        return 0
    return len(re.findall(r"^\d+\. ", section.group(1), re.M))


def checks(root: Path):
    text = {f: (root / f).read_text(encoding="utf-8") for f in FILES}
    skill, rules, readme = text[FILES[0]], text[FILES[1]], text[FILES[2]]
    results = []

    m = re.search(r"Copy the (\w+) rules", readme)
    said = NUMBER_WORDS.get(m.group(1).lower()) if m else None
    have = rule_count(skill)
    results.append(
        ("C1", said == have, f"{have} rules in SKILL.md, README says {said}")
    )

    m = re.search(r"SKILL\.md\]\([^)]*\), (\d+) lines", readme)
    said = int(m.group(1)) if m else None
    have = len(skill.splitlines())
    results.append(
        ("C2", said == have, f"SKILL.md is {have} lines, README says {said}")
    )

    plugin = json.loads(text[FILES[3]])["description"]
    market = json.loads(text[FILES[4]])["plugins"][0]["description"]
    problems = []
    if plugin != market:
        problems.append("plugin.json and marketplace.json descriptions differ")
    if "every fact" in plugin or "every fact" in market:
        problems.append("description promises every fact")
    problems += lint_text(plugin)[0]
    results.append(
        ("C3", not problems, "; ".join(problems) or "one description, lint clean")
    )

    wrong = [
        f
        for f in (FILES[0], FILES[1], FILES[5], FILES[6])
        if "three nouns" not in text[f] or "three words" in text[f]
    ]
    results.append(
        ("C4", not wrong, ", ".join(wrong) or "rule 7 counts nouns everywhere")
    )

    errors = [f"{FILES[0]}: {e}" for e in lint_text(skill)[0]]
    errors += [f"{FILES[1]}: {e}" for e in lint_text(rules)[0]]
    results.append(("C5", not errors, "; ".join(errors) or "skill prose lints clean"))
    return results


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    root = Path(argv[0]) if argv else REPO
    ok = True
    for cid, passed, message in checks(root):
        print(f"{'ok  ' if passed else 'FAIL'} {cid} {message}")
        ok = ok and passed
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
