#!/usr/bin/env python3
"""Validate the shipped skill against the platform's hard constraints.

Checks skills/ste-explain/SKILL.md:
  - frontmatter present, with single-line name: and description:
  - name: <=64 chars, [a-z0-9-] only, no "claude"/"anthropic"
  - description: non-empty, <=1024 chars
  - body <=150 lines (warn at 120)
  - every references/ file mentioned in the body exists

Exit codes: 0 ok, 1 violations.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILL_DIR = REPO / "skills" / "ste-explain"
SKILL_MD = SKILL_DIR / "SKILL.md"
BODY_LINE_LIMIT = 150
BODY_LINE_WARN = 120


def main():
    errors, warnings = [], []
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else SKILL_MD
    if not path.exists():
        print(f"ERROR   {path} not found")
        return 1
    text = path.read_text(encoding="utf-8")

    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not m:
        print("ERROR   no YAML frontmatter block")
        return 1
    front, body = m.group(1), m.group(2)

    fields = {}
    for line in front.splitlines():
        km = re.match(r"^(\w[\w-]*):\s*(.*)$", line)
        if km:
            fields[km.group(1)] = km.group(2).strip()
        elif line.strip():
            errors.append(f"frontmatter line not 'key: value' "
                          f"(multiline values not allowed): {line!r}")

    name = fields.get("name", "")
    desc = fields.get("description", "")
    if not name:
        errors.append("missing name")
    else:
        if len(name) > 64:
            errors.append(f"name is {len(name)} chars (limit 64)")
        if not re.fullmatch(r"[a-z0-9-]+", name):
            errors.append("name must be lowercase letters, digits, hyphens")
        if "claude" in name.lower() or "anthropic" in name.lower():
            errors.append("name must not contain 'claude' or 'anthropic'")
    if not desc:
        errors.append("missing or empty description")
    elif len(desc) > 1024:
        errors.append(f"description is {len(desc)} chars (limit 1024)")

    body_lines = body.count("\n") + 1
    if body_lines > BODY_LINE_LIMIT:
        errors.append(f"body is {body_lines} lines (limit {BODY_LINE_LIMIT})")
    elif body_lines > BODY_LINE_WARN:
        warnings.append(f"body is {body_lines} lines (keep it lean)")

    for ref in re.findall(r"references/[\w./-]+\.md", body):
        if not (path.parent / ref).exists():
            errors.append(f"body mentions {ref} but the file does not exist")

    for e in errors:
        print(f"ERROR   {e}")
    for w in warnings:
        print(f"warning {w}")
    if not errors:
        print(f"ok: name={name!r}, description {len(desc)} chars, "
              f"body {body_lines} lines")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
